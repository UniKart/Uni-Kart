import React, { useState, useEffect } from 'react';
import './App.css';
import { Card, CardHeader, CardTitle, CardContent } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Label } from './components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Badge } from './components/ui/badge';
import { Separator } from './components/ui/separator';
import { Calculator, TrendingUp, MapPin, User, Euro, PieChart, Lightbulb } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

function App() {
  // Form state
  const [formData, setFormData] = useState({
    gross_income: '',
    employment_type: 'employee',
    region: '',
    province: '',
    city: ''
  });

  // Location data
  const [regions, setRegions] = useState([]);
  const [provinces, setProvinces] = useState([]);
  const [cities, setCities] = useState([]);

  // Results
  const [taxResult, setTaxResult] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [optimizationTips, setOptimizationTips] = useState([]);

  // Comparison form
  const [comparisonIncome, setComparisonIncome] = useState('');

  // Loading states
  const [loading, setLoading] = useState(false);
  const [loadingComparison, setLoadingComparison] = useState(false);

  // Fetch regions on component mount
  useEffect(() => {
    fetchRegions();
  }, []);

  // Fetch provinces when region changes
  useEffect(() => {
    if (formData.region) {
      fetchProvinces(formData.region);
      setFormData(prev => ({ ...prev, province: '', city: '' }));
    }
  }, [formData.region]);

  // Fetch cities when province changes
  useEffect(() => {
    if (formData.region && formData.province) {
      fetchCities(formData.region, formData.province);
      setFormData(prev => ({ ...prev, city: '' }));
    }
  }, [formData.province]);

  const fetchRegions = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/regions`);
      const data = await response.json();
      setRegions(data.regions);
    } catch (error) {
      console.error('Error fetching regions:', error);
    }
  };

  const fetchProvinces = async (region) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/provinces/${region}`);
      const data = await response.json();
      setProvinces(data.provinces);
    } catch (error) {
      console.error('Error fetching provinces:', error);
    }
  };

  const fetchCities = async (region, province) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/cities/${region}/${province}`);
      const data = await response.json();
      setCities(data.cities);
    } catch (error) {
      console.error('Error fetching cities:', error);
    }
  };

  const calculateTax = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/calculate-tax`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          gross_income: parseFloat(formData.gross_income)
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setTaxResult(result);
        
        // Fetch optimization tips
        const tipsResponse = await fetch(`${BACKEND_URL}/api/tax-optimization/${formData.gross_income}`);
        if (tipsResponse.ok) {
          const tipsData = await tipsResponse.json();
          setOptimizationTips(tipsData.optimization_tips);
        }
      } else {
        console.error('Tax calculation failed');
      }
    } catch (error) {
      console.error('Error calculating tax:', error);
    }
    setLoading(false);
  };

  const compareIncome = async () => {
    if (!comparisonIncome || !taxResult) return;
    
    setLoadingComparison(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/compare-income`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_income: parseFloat(formData.gross_income),
          comparison_income: parseFloat(comparisonIncome),
          employment_type: formData.employment_type,
          region: formData.region,
          province: formData.province,
          city: formData.city
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setComparison(result);
      }
    } catch (error) {
      console.error('Error comparing income:', error);
    }
    setLoadingComparison(false);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const getEmploymentTypeLabel = (type) => {
    const labels = {
      employee: 'Dipendente',
      freelancer: 'Libero Professionista',
      pensioner: 'Pensionato'
    };
    return labels[type] || type;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl text-white">
              <Calculator className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Calcolatore Tasse Italia 2025</h1>
              <p className="text-sm text-slate-600">Calcolo IRPEF, INPS e addizionali regionali/comunali</p>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Input Form */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24 shadow-lg border-0 bg-white/90 backdrop-blur-sm">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-slate-900">
                  <User className="w-5 h-5 text-blue-600" />
                  Dati Contributore
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Income */}
                <div className="space-y-2">
                  <Label htmlFor="income" className="text-sm font-medium text-slate-700">
                    Reddito Annuo Lordo (€)
                  </Label>
                  <div className="relative">
                    <Euro className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                    <Input
                      id="income"
                      type="number"
                      placeholder="es. 35000"
                      value={formData.gross_income}
                      onChange={(e) => setFormData(prev => ({ ...prev, gross_income: e.target.value }))}
                      className="pl-10 h-11 bg-white border-slate-200 focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>
                </div>

                {/* Employment Type */}
                <div className="space-y-2">
                  <Label className="text-sm font-medium text-slate-700">Tipo di Impiego</Label>
                  <Select value={formData.employment_type} onValueChange={(value) => setFormData(prev => ({ ...prev, employment_type: value }))}>
                    <SelectTrigger className="h-11 bg-white border-slate-200">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="employee">Dipendente</SelectItem>
                      <SelectItem value="freelancer">Libero Professionista</SelectItem>
                      <SelectItem value="pensioner">Pensionato</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Location */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-blue-600" />
                    <Label className="text-sm font-medium text-slate-700">Località di Residenza</Label>
                  </div>
                  
                  {/* Region */}
                  <Select value={formData.region} onValueChange={(value) => setFormData(prev => ({ ...prev, region: value }))}>
                    <SelectTrigger className="h-11 bg-white border-slate-200">
                      <SelectValue placeholder="Seleziona regione" />
                    </SelectTrigger>
                    <SelectContent>
                      {regions.map((region) => (
                        <SelectItem key={region} value={region}>{region}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  {/* Province */}
                  <Select value={formData.province} onValueChange={(value) => setFormData(prev => ({ ...prev, province: value }))} disabled={!formData.region}>
                    <SelectTrigger className="h-11 bg-white border-slate-200">
                      <SelectValue placeholder="Seleziona provincia" />
                    </SelectTrigger>
                    <SelectContent>
                      {provinces.map((province) => (
                        <SelectItem key={province} value={province}>{province}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  {/* City */}
                  <Select value={formData.city} onValueChange={(value) => setFormData(prev => ({ ...prev, city: value }))} disabled={!formData.province}>
                    <SelectTrigger className="h-11 bg-white border-slate-200">
                      <SelectValue placeholder="Seleziona città" />
                    </SelectTrigger>
                    <SelectContent>
                      {cities.map((city) => (
                        <SelectItem key={city} value={city}>{city}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Calculate Button */}
                <Button 
                  onClick={calculateTax}
                  disabled={!formData.gross_income || !formData.region || !formData.province || !formData.city || loading}
                  className="w-full h-11 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium transition-all duration-300"
                >
                  {loading ? 'Calcolo in corso...' : 'Calcola Tasse'}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Results */}
          <div className="lg:col-span-2">
            {taxResult ? (
              <Tabs defaultValue="results" className="space-y-6">
                <TabsList className="grid w-full grid-cols-3 bg-white/80 backdrop-blur-sm">
                  <TabsTrigger value="results" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">
                    <PieChart className="w-4 h-4 mr-2" />
                    Risultati
                  </TabsTrigger>
                  <TabsTrigger value="comparison" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">
                    <TrendingUp className="w-4 h-4 mr-2" />
                    Confronto
                  </TabsTrigger>
                  <TabsTrigger value="optimization" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">
                    <Lightbulb className="w-4 h-4 mr-2" />
                    Ottimizzazione
                  </TabsTrigger>
                </TabsList>

                {/* Tax Results */}
                <TabsContent value="results" className="space-y-6">
                  <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
                    <CardHeader className="pb-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-slate-900">Calcolo Tasse 2025</CardTitle>
                          <p className="text-sm text-slate-600 mt-1">
                            {getEmploymentTypeLabel(formData.employment_type)} • {formData.city}, {formData.province} ({formData.region})
                          </p>
                        </div>
                        <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                          Aliquota Effettiva: {taxResult.effective_tax_rate}%
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {/* Main Results Grid */}
                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="space-y-3">
                          <div className="flex justify-between py-2">
                            <span className="text-slate-600">Reddito Annuo Lordo:</span>
                            <span className="font-semibold text-slate-900">{formatCurrency(taxResult.gross_income)}</span>
                          </div>
                          <div className="flex justify-between py-2">
                            <span className="text-slate-600">Contributi INPS:</span>
                            <span className="font-semibold text-red-600">-{formatCurrency(taxResult.inps_contributions)}</span>
                          </div>
                          <div className="flex justify-between py-2">
                            <span className="text-slate-600">Reddito Imponibile:</span>
                            <span className="font-semibold text-slate-900">{formatCurrency(taxResult.taxable_income)}</span>
                          </div>
                          <div className="flex justify-between py-2">
                            <span className="text-slate-600">Detrazione Lavoro:</span>
                            <span className="font-semibold text-green-600">-{formatCurrency(taxResult.employee_deduction)}</span>
                          </div>
                        </div>

                        <div className="space-y-3">
                          <div className="flex justify-between py-2">
                            <span className="text-slate-600">Imposta IRPEF:</span>
                            <span className="font-semibold text-red-600">-{formatCurrency(taxResult.irpef_tax)}</span>
                          </div>
                          <div className="flex justify-between py-2">
                            <span className="text-slate-600">Addizionale Regionale:</span>
                            <span className="font-semibold text-red-600">-{formatCurrency(taxResult.regional_surtax)}</span>
                          </div>
                          <div className="flex justify-between py-2">
                            <span className="text-slate-600">Addizionale Comunale:</span>
                            <span className="font-semibold text-red-600">-{formatCurrency(taxResult.municipal_surtax)}</span>
                          </div>
                          <div className="flex justify-between py-2">
                            <span className="text-slate-600">Totale Imposte:</span>
                            <span className="font-semibold text-red-600">-{formatCurrency(taxResult.total_tax_payable)}</span>
                          </div>
                        </div>
                      </div>

                      <Separator />

                      {/* Final Results */}
                      <div className="grid md:grid-cols-2 gap-4 pt-2">
                        <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
                          <p className="text-sm text-green-700 font-medium">Reddito Netto Annuale</p>
                          <p className="text-2xl font-bold text-green-800">{formatCurrency(taxResult.net_annual_income)}</p>
                        </div>
                        <div className="p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border border-blue-200">
                          <p className="text-sm text-blue-700 font-medium">Reddito Netto Mensile</p>
                          <p className="text-2xl font-bold text-blue-800">{formatCurrency(taxResult.net_monthly_income)}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Income Comparison */}
                <TabsContent value="comparison" className="space-y-6">
                  <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle>Confronto Redditi</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex gap-3">
                        <div className="flex-1">
                          <Label className="text-sm font-medium text-slate-700">Reddito da Confrontare (€)</Label>
                          <Input
                            type="number"
                            placeholder="es. 40000"
                            value={comparisonIncome}
                            onChange={(e) => setComparisonIncome(e.target.value)}
                            className="mt-1 h-11 bg-white border-slate-200"
                          />
                        </div>
                        <div className="flex items-end">
                          <Button 
                            onClick={compareIncome}
                            disabled={!comparisonIncome || loadingComparison}
                            className="h-11 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                          >
                            {loadingComparison ? 'Confronto...' : 'Confronta'}
                          </Button>
                        </div>
                      </div>

                      {comparison && (
                        <div className="mt-6 space-y-4">
                          <div className="grid md:grid-cols-2 gap-4">
                            <div className="p-4 bg-slate-50 rounded-lg">
                              <h4 className="font-semibold text-slate-900 mb-3">Reddito Attuale</h4>
                              <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                  <span>Lordo:</span>
                                  <span>{formatCurrency(comparison.current.gross_income)}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Netto:</span>
                                  <span className="font-semibold text-green-600">{formatCurrency(comparison.current.net_annual_income)}</span>
                                </div>
                              </div>
                            </div>

                            <div className="p-4 bg-blue-50 rounded-lg">
                              <h4 className="font-semibold text-slate-900 mb-3">Reddito Confronto</h4>
                              <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                  <span>Lordo:</span>
                                  <span>{formatCurrency(comparison.comparison.gross_income)}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Netto:</span>
                                  <span className="font-semibold text-green-600">{formatCurrency(comparison.comparison.net_annual_income)}</span>
                                </div>
                              </div>
                            </div>
                          </div>

                          <div className="p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200">
                            <h4 className="font-semibold text-slate-900 mb-3">Differenze</h4>
                            <div className="grid md:grid-cols-3 gap-4 text-sm">
                              <div>
                                <span className="text-slate-600">Differenza Netta:</span>
                                <p className="font-bold text-lg text-slate-900">{formatCurrency(comparison.differences.net_difference)}</p>
                              </div>
                              <div>
                                <span className="text-slate-600">Differenza Tasse:</span>
                                <p className="font-bold text-lg text-red-600">{formatCurrency(comparison.differences.tax_difference)}</p>
                              </div>
                              <div>
                                <span className="text-slate-600">Aliquota Marginale:</span>
                                <p className="font-bold text-lg text-orange-600">{comparison.differences.marginal_tax_rate}%</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Optimization Tips */}
                <TabsContent value="optimization" className="space-y-6">
                  <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Lightbulb className="w-5 h-5 text-yellow-600" />
                        Suggerimenti per l'Ottimizzazione Fiscale
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {optimizationTips.map((tip, index) => (
                          <div key={index} className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                            <div className="flex justify-between items-start mb-2">
                              <Badge variant="secondary" className="bg-blue-100 text-blue-800">{tip.category}</Badge>
                              <span className="text-sm text-green-600 font-medium">{tip.potential_savings}</span>
                            </div>
                            <p className="text-slate-700">{tip.tip}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            ) : (
              <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm h-96 flex items-center justify-center">
                <div className="text-center text-slate-500">
                  <Calculator className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                  <p>Inserisci i tuoi dati per calcolare le tasse</p>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;