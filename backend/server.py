from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
from decimal import Decimal, ROUND_HALF_UP
import uvicorn

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TaxCalculationRequest(BaseModel):
    gross_income: float
    employment_type: str  # "employee", "freelancer", "pensioner"
    region: str
    province: str
    city: str

class TaxResult(BaseModel):
    gross_income: float
    inps_contributions: float
    taxable_income: float
    irpef_tax: float
    regional_surtax: float
    municipal_surtax: float
    total_tax_payable: float
    net_annual_income: float
    net_monthly_income: float
    employee_deduction: float
    effective_tax_rate: float

class ComparisonRequest(BaseModel):
    current_income: float
    comparison_income: float
    employment_type: str
    region: str
    province: str
    city: str

# Italian regions and provinces with tax rates (2025)
ITALIAN_TAX_RATES = {
    "Lombardia": {
        "regional_rate": 1.73,
        "provinces": {
            "Milano": {"municipal_rates": {"Milano": 0.8, "Monza": 0.6, "Como": 0.5}},
            "Bergamo": {"municipal_rates": {"Bergamo": 0.7, "Treviglio": 0.5}},
            "Brescia": {"municipal_rates": {"Brescia": 0.6, "Desenzano del Garda": 0.4}},
            "Varese": {"municipal_rates": {"Varese": 0.5, "Busto Arsizio": 0.6}},
            "Pavia": {"municipal_rates": {"Pavia": 0.5, "Vigevano": 0.4}},
        }
    },
    "Lazio": {
        "regional_rate": 3.33,
        "provinces": {
            "Roma": {"municipal_rates": {"Roma": 0.9, "Guidonia": 0.8, "Fiumicino": 0.7}},
            "Latina": {"municipal_rates": {"Latina": 0.8, "Aprilia": 0.6}},
            "Frosinone": {"municipal_rates": {"Frosinone": 0.7, "Cassino": 0.5}},
        }
    },
    "Veneto": {
        "regional_rate": 1.23,
        "provinces": {
            "Venezia": {"municipal_rates": {"Venezia": 0.8, "Mestre": 0.8, "Mira": 0.6}},
            "Verona": {"municipal_rates": {"Verona": 0.7, "Legnago": 0.5}},
            "Padova": {"municipal_rates": {"Padova": 0.8, "Cittadella": 0.5}},
            "Vicenza": {"municipal_rates": {"Vicenza": 0.6, "Bassano del Grappa": 0.5}},
        }
    },
    "Piemonte": {
        "regional_rate": 3.33,
        "provinces": {
            "Torino": {"municipal_rates": {"Torino": 0.8, "Moncalieri": 0.7, "Rivoli": 0.6}},
            "Cuneo": {"municipal_rates": {"Cuneo": 0.6, "Alba": 0.5}},
            "Asti": {"municipal_rates": {"Asti": 0.7, "Nizza Monferrato": 0.5}},
        }
    },
    "Campania": {
        "regional_rate": 3.33,
        "provinces": {
            "Napoli": {"municipal_rates": {"Napoli": 0.8, "Pozzuoli": 0.7, "Torre del Greco": 0.6}},
            "Salerno": {"municipal_rates": {"Salerno": 0.7, "Battipaglia": 0.6}},
            "Caserta": {"municipal_rates": {"Caserta": 0.6, "Aversa": 0.5}},
        }
    },
    "Emilia-Romagna": {
        "regional_rate": 2.03,
        "provinces": {
            "Bologna": {"municipal_rates": {"Bologna": 0.8, "Imola": 0.6, "San Lazzaro": 0.5}},
            "Modena": {"municipal_rates": {"Modena": 0.7, "Carpi": 0.6}},
            "Parma": {"municipal_rates": {"Parma": 0.6, "Fidenza": 0.5}},
            "Reggio Emilia": {"municipal_rates": {"Reggio Emilia": 0.7, "Correggio": 0.5}},
        }
    },
    "Toscana": {
        "regional_rate": 2.03,
        "provinces": {
            "Firenze": {"municipal_rates": {"Firenze": 0.3, "Scandicci": 0.5, "Sesto Fiorentino": 0.4}},
            "Pisa": {"municipal_rates": {"Pisa": 0.6, "Pontedera": 0.5}},
            "Livorno": {"municipal_rates": {"Livorno": 0.7, "Piombino": 0.6}},
            "Siena": {"municipal_rates": {"Siena": 0.5, "Poggibonsi": 0.4}},
        }
    },
}

def calculate_inps_contributions(gross_income: float, employment_type: str) -> float:
    """Calculate INPS social security contributions"""
    if employment_type == "employee":
        # Employee pays about 9.19% for pension + 0.30% for unemployment
        return round(gross_income * 0.0949, 2)
    elif employment_type == "freelancer":
        # Freelancers pay higher rates, approximately 24%
        return round(gross_income * 0.24, 2)
    elif employment_type == "pensioner":
        # Pensioners don't pay INPS on pension income
        return 0.0
    return 0.0

def calculate_employee_deduction(gross_income: float, employment_type: str) -> float:
    """Calculate standard employee tax deduction (detrazione per lavoro dipendente)"""
    if employment_type == "employee":
        if gross_income <= 15000:
            return 1955.0
        elif gross_income <= 28000:
            # Progressive reduction from 1955 to 1910
            return round(1955 - ((gross_income - 15000) / 13000) * 45, 2)
        elif gross_income <= 50000:
            # Further reduction
            return round(1910 - ((gross_income - 28000) / 22000) * 910, 2)
        else:
            return 1000.0
    elif employment_type == "pensioner":
        if gross_income <= 7500:
            return 1725.0
        elif gross_income <= 15000:
            return round(1725 - ((gross_income - 7500) / 7500) * 725, 2)
        else:
            return 1000.0
    return 0.0

def calculate_irpef_tax(taxable_income: float) -> float:
    """Calculate IRPEF tax based on 2025 progressive brackets"""
    if taxable_income <= 0:
        return 0.0
    
    tax = 0.0
    
    # 2025 IRPEF brackets
    if taxable_income <= 28000:
        tax = taxable_income * 0.23
    elif taxable_income <= 50000:
        tax = 28000 * 0.23 + (taxable_income - 28000) * 0.35
    else:
        tax = 28000 * 0.23 + 22000 * 0.35 + (taxable_income - 50000) * 0.43
    
    return round(tax, 2)

def calculate_surtaxes(taxable_income: float, region: str, province: str, city: str) -> tuple:
    """Calculate regional and municipal surtaxes"""
    if taxable_income <= 0:
        return 0.0, 0.0
    
    # Get regional rate
    regional_rate = ITALIAN_TAX_RATES.get(region, {}).get("regional_rate", 2.3)
    regional_surtax = round(taxable_income * (regional_rate / 100), 2)
    
    # Get municipal rate
    municipal_rate = 0.6  # Default
    if region in ITALIAN_TAX_RATES:
        provinces = ITALIAN_TAX_RATES[region]["provinces"]
        if province in provinces:
            municipal_rates = provinces[province]["municipal_rates"]
            municipal_rate = municipal_rates.get(city, 0.6)
    
    municipal_surtax = round(taxable_income * (municipal_rate / 100), 2)
    
    return regional_surtax, municipal_surtax

@app.get("/api/regions")
async def get_regions():
    """Get list of Italian regions"""
    return {"regions": list(ITALIAN_TAX_RATES.keys())}

@app.get("/api/provinces/{region}")
async def get_provinces(region: str):
    """Get provinces for a specific region"""
    if region not in ITALIAN_TAX_RATES:
        raise HTTPException(status_code=404, detail="Region not found")
    
    provinces = list(ITALIAN_TAX_RATES[region]["provinces"].keys())
    return {"provinces": provinces}

@app.get("/api/cities/{region}/{province}")
async def get_cities(region: str, province: str):
    """Get cities for a specific province"""
    if region not in ITALIAN_TAX_RATES:
        raise HTTPException(status_code=404, detail="Region not found")
    
    provinces = ITALIAN_TAX_RATES[region]["provinces"]
    if province not in provinces:
        raise HTTPException(status_code=404, detail="Province not found")
    
    cities = list(provinces[province]["municipal_rates"].keys())
    return {"cities": cities}

@app.post("/api/calculate-tax", response_model=TaxResult)
async def calculate_tax(request: TaxCalculationRequest):
    """Calculate Italian taxes for 2025"""
    try:
        gross_income = request.gross_income
        
        # Calculate INPS contributions
        inps_contributions = calculate_inps_contributions(gross_income, request.employment_type)
        
        # Calculate taxable income (gross - INPS)
        taxable_income = gross_income - inps_contributions
        
        # Calculate employee deduction
        employee_deduction = calculate_employee_deduction(gross_income, request.employment_type)
        
        # Calculate IRPEF tax
        irpef_before_deduction = calculate_irpef_tax(taxable_income)
        irpef_tax = max(0, irpef_before_deduction - employee_deduction)
        
        # Calculate surtaxes
        regional_surtax, municipal_surtax = calculate_surtaxes(
            taxable_income, request.region, request.province, request.city
        )
        
        # Calculate totals
        total_tax_payable = irpef_tax + regional_surtax + municipal_surtax
        net_annual_income = gross_income - inps_contributions - total_tax_payable
        net_monthly_income = round(net_annual_income / 12, 2)
        
        # Calculate effective tax rate
        effective_tax_rate = round((total_tax_payable / gross_income) * 100, 2) if gross_income > 0 else 0
        
        return TaxResult(
            gross_income=gross_income,
            inps_contributions=inps_contributions,
            taxable_income=taxable_income,
            irpef_tax=irpef_tax,
            regional_surtax=regional_surtax,
            municipal_surtax=municipal_surtax,
            total_tax_payable=total_tax_payable,
            net_annual_income=net_annual_income,
            net_monthly_income=net_monthly_income,
            employee_deduction=employee_deduction,
            effective_tax_rate=effective_tax_rate
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/compare-income")
async def compare_income(request: ComparisonRequest):
    """Compare tax implications of different income levels"""
    try:
        # Calculate for current income
        current_request = TaxCalculationRequest(
            gross_income=request.current_income,
            employment_type=request.employment_type,
            region=request.region,
            province=request.province,
            city=request.city
        )
        current_result = await calculate_tax(current_request)
        
        # Calculate for comparison income
        comparison_request = TaxCalculationRequest(
            gross_income=request.comparison_income,
            employment_type=request.employment_type,
            region=request.region,
            province=request.province,
            city=request.city
        )
        comparison_result = await calculate_tax(comparison_request)
        
        # Calculate differences
        income_difference = request.comparison_income - request.current_income
        tax_difference = comparison_result.total_tax_payable - current_result.total_tax_payable
        net_difference = comparison_result.net_annual_income - current_result.net_annual_income
        marginal_rate = round((tax_difference / income_difference) * 100, 2) if income_difference != 0 else 0
        
        return {
            "current": current_result,
            "comparison": comparison_result,
            "differences": {
                "income_difference": income_difference,
                "tax_difference": tax_difference,
                "net_difference": net_difference,
                "marginal_tax_rate": marginal_rate
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/tax-optimization/{income}")
async def get_tax_optimization_tips(income: float):
    """Get tax optimization suggestions based on income level"""
    tips = []
    
    if income > 50000:
        tips.append({
            "category": "High Income",
            "tip": "Consider contributing to a complementary pension fund (fondo pensione) to reduce taxable income",
            "potential_savings": "Up to €5,164 annual deduction"
        })
        tips.append({
            "category": "Investments",
            "tip": "Evaluate tax-efficient investment options like PIR (Individual Savings Plans)",
            "potential_savings": "Tax-free capital gains up to certain limits"
        })
    
    if income > 28000:
        tips.append({
            "category": "Deductions",
            "tip": "Maximize deductible expenses like medical costs, mortgage interest, and charitable donations",
            "potential_savings": "Variable based on expenses"
        })
    
    tips.append({
        "category": "Employment",
        "tip": "Consider salary sacrifice schemes or benefit packages to optimize total compensation",
        "potential_savings": "Potential tax savings on benefits"
    })
    
    tips.append({
        "category": "Location",
        "tip": "Be aware of regional differences - some regions have lower surtax rates",
        "potential_savings": "Up to 2% difference in regional rates"
    })
    
    return {"optimization_tips": tips}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)