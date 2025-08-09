import requests
import sys
import json
from datetime import datetime

class ItalianTaxCalculatorTester:
    def __init__(self, base_url="https://bfe0ea7f-8ff9-4f1c-bf7a-a3af73cd6912.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, expected_keys=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    
                    # Check for expected keys if provided
                    if expected_keys:
                        for key in expected_keys:
                            if key not in response_data:
                                print(f"   ❌ Missing expected key: {key}")
                                success = False
                                break
                    
                    if success:
                        self.tests_passed += 1
                        print(f"✅ Passed - {name}")
                        return True, response_data
                    else:
                        print(f"❌ Failed - Missing expected keys")
                        return False, {}
                        
                except json.JSONDecodeError:
                    print(f"   Response Text: {response.text[:200]}...")
                    if expected_status == 200:
                        print(f"❌ Failed - Invalid JSON response")
                        return False, {}
                    else:
                        self.tests_passed += 1
                        print(f"✅ Passed - {name}")
                        return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_regions_endpoint(self):
        """Test /api/regions endpoint"""
        return self.run_test(
            "Get Regions",
            "GET",
            "api/regions",
            200,
            expected_keys=["regions"]
        )

    def test_provinces_endpoint(self, region="Lombardia"):
        """Test /api/provinces/{region} endpoint"""
        return self.run_test(
            f"Get Provinces for {region}",
            "GET",
            f"api/provinces/{region}",
            200,
            expected_keys=["provinces"]
        )

    def test_cities_endpoint(self, region="Lombardia", province="Milano"):
        """Test /api/cities/{region}/{province} endpoint"""
        return self.run_test(
            f"Get Cities for {province}, {region}",
            "GET",
            f"api/cities/{region}/{province}",
            200,
            expected_keys=["cities"]
        )

    def test_calculate_tax_employee(self):
        """Test tax calculation for employee"""
        test_data = {
            "gross_income": 35000,
            "employment_type": "employee",
            "region": "Lombardia",
            "province": "Milano",
            "city": "Milano"
        }
        
        expected_keys = [
            "gross_income", "inps_contributions", "taxable_income", 
            "irpef_tax", "regional_surtax", "municipal_surtax",
            "total_tax_payable", "net_annual_income", "net_monthly_income",
            "employee_deduction", "effective_tax_rate"
        ]
        
        return self.run_test(
            "Calculate Tax - Employee (35k EUR)",
            "POST",
            "api/calculate-tax",
            200,
            data=test_data,
            expected_keys=expected_keys
        )

    def test_calculate_tax_freelancer(self):
        """Test tax calculation for freelancer"""
        test_data = {
            "gross_income": 50000,
            "employment_type": "freelancer",
            "region": "Lazio",
            "province": "Roma",
            "city": "Roma"
        }
        
        expected_keys = [
            "gross_income", "inps_contributions", "taxable_income", 
            "irpef_tax", "regional_surtax", "municipal_surtax",
            "total_tax_payable", "net_annual_income", "net_monthly_income",
            "employee_deduction", "effective_tax_rate"
        ]
        
        return self.run_test(
            "Calculate Tax - Freelancer (50k EUR)",
            "POST",
            "api/calculate-tax",
            200,
            data=test_data,
            expected_keys=expected_keys
        )

    def test_calculate_tax_pensioner(self):
        """Test tax calculation for pensioner"""
        test_data = {
            "gross_income": 25000,
            "employment_type": "pensioner",
            "region": "Veneto",
            "province": "Venezia",
            "city": "Venezia"
        }
        
        expected_keys = [
            "gross_income", "inps_contributions", "taxable_income", 
            "irpef_tax", "regional_surtax", "municipal_surtax",
            "total_tax_payable", "net_annual_income", "net_monthly_income",
            "employee_deduction", "effective_tax_rate"
        ]
        
        return self.run_test(
            "Calculate Tax - Pensioner (25k EUR)",
            "POST",
            "api/calculate-tax",
            200,
            data=test_data,
            expected_keys=expected_keys
        )

    def test_compare_income(self):
        """Test income comparison endpoint"""
        test_data = {
            "current_income": 35000,
            "comparison_income": 45000,
            "employment_type": "employee",
            "region": "Lombardia",
            "province": "Milano",
            "city": "Milano"
        }
        
        expected_keys = ["current", "comparison", "differences"]
        
        return self.run_test(
            "Compare Income (35k vs 45k EUR)",
            "POST",
            "api/compare-income",
            200,
            data=test_data,
            expected_keys=expected_keys
        )

    def test_tax_optimization(self, income=35000):
        """Test tax optimization endpoint"""
        return self.run_test(
            f"Tax Optimization Tips ({income} EUR)",
            "GET",
            f"api/tax-optimization/{income}",
            200,
            expected_keys=["optimization_tips"]
        )

    def test_edge_cases(self):
        """Test edge cases"""
        print("\n🧪 Testing Edge Cases...")
        
        # Test very low income
        low_income_data = {
            "gross_income": 10000,
            "employment_type": "employee",
            "region": "Lombardia",
            "province": "Milano",
            "city": "Milano"
        }
        
        success1, result1 = self.run_test(
            "Low Income (10k EUR)",
            "POST",
            "api/calculate-tax",
            200,
            data=low_income_data
        )
        
        # Test high income
        high_income_data = {
            "gross_income": 80000,
            "employment_type": "employee",
            "region": "Lombardia",
            "province": "Milano",
            "city": "Milano"
        }
        
        success2, result2 = self.run_test(
            "High Income (80k EUR)",
            "POST",
            "api/calculate-tax",
            200,
            data=high_income_data
        )
        
        # Test zero income
        zero_income_data = {
            "gross_income": 0,
            "employment_type": "employee",
            "region": "Lombardia",
            "province": "Milano",
            "city": "Milano"
        }
        
        success3, result3 = self.run_test(
            "Zero Income",
            "POST",
            "api/calculate-tax",
            200,
            data=zero_income_data
        )
        
        return success1 and success2 and success3

    def validate_tax_calculations(self):
        """Validate tax calculation logic"""
        print("\n🧮 Validating Tax Calculation Logic...")
        
        # Test employee with 35k income
        test_data = {
            "gross_income": 35000,
            "employment_type": "employee",
            "region": "Lombardia",
            "province": "Milano",
            "city": "Milano"
        }
        
        success, result = self.run_test(
            "Validation - Employee 35k",
            "POST",
            "api/calculate-tax",
            200,
            data=test_data
        )
        
        if success and result:
            print("\n📊 Calculation Breakdown:")
            print(f"   Gross Income: €{result['gross_income']:,.2f}")
            print(f"   INPS Contributions: €{result['inps_contributions']:,.2f} ({result['inps_contributions']/result['gross_income']*100:.2f}%)")
            print(f"   Taxable Income: €{result['taxable_income']:,.2f}")
            print(f"   Employee Deduction: €{result['employee_deduction']:,.2f}")
            print(f"   IRPEF Tax: €{result['irpef_tax']:,.2f}")
            print(f"   Regional Surtax: €{result['regional_surtax']:,.2f}")
            print(f"   Municipal Surtax: €{result['municipal_surtax']:,.2f}")
            print(f"   Total Tax: €{result['total_tax_payable']:,.2f}")
            print(f"   Net Annual: €{result['net_annual_income']:,.2f}")
            print(f"   Net Monthly: €{result['net_monthly_income']:,.2f}")
            print(f"   Effective Rate: {result['effective_tax_rate']:.2f}%")
            
            # Validate INPS rate for employee (should be ~9.49%)
            expected_inps_rate = 9.49
            actual_inps_rate = (result['inps_contributions'] / result['gross_income']) * 100
            if abs(actual_inps_rate - expected_inps_rate) < 0.1:
                print(f"✅ INPS rate validation passed: {actual_inps_rate:.2f}%")
            else:
                print(f"❌ INPS rate validation failed: expected ~{expected_inps_rate}%, got {actual_inps_rate:.2f}%")
                
        return success

def main():
    print("🇮🇹 Italian Tax Calculator API Testing")
    print("=" * 50)
    
    tester = ItalianTaxCalculatorTester()
    
    # Test all endpoints
    tests = [
        tester.test_regions_endpoint,
        lambda: tester.test_provinces_endpoint("Lombardia"),
        lambda: tester.test_cities_endpoint("Lombardia", "Milano"),
        tester.test_calculate_tax_employee,
        tester.test_calculate_tax_freelancer,
        tester.test_calculate_tax_pensioner,
        tester.test_compare_income,
        lambda: tester.test_tax_optimization(35000),
        lambda: tester.test_tax_optimization(60000),
        tester.test_edge_cases,
        tester.validate_tax_calculations
    ]
    
    # Run all tests
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            tester.tests_run += 1
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All backend tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())