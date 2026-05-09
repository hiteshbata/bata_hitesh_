'use client';

import { Activity, Droplets, MapPin, ShieldAlert } from 'lucide-react';

export default function InsightsPage() {
  // For MVP, we present a mock visualization dashboard of aggregated insights

  const mockInsights = [
    { village: 'Rajkot', risk: 'high', waterStress: true, ndvi: 0.35, action: 'Urgent irrigation needed. Severe heat stress detected.' },
    { village: 'Bhuj', risk: 'medium', waterStress: false, ndvi: 0.55, action: 'Normal monitoring. Next irrigation in 5 days.' },
    { village: 'Surat', risk: 'low', waterStress: false, ndvi: 0.82, action: 'Crop healthy. Ideal NDVI levels for this season.' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">Crop Health Insights</h2>
          <p className="text-gray-500 mt-1">Aggregated satellite NDVI & AI risk analysis</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="col-span-2 bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-green-600" /> Average NDVI Heatmap
          </h3>
          <div className="h-64 w-full bg-gray-100 rounded-lg flex flex-col items-center justify-center border-2 border-dashed border-gray-200">
            <MapPin className="w-8 h-8 text-gray-400 mb-2" />
            <p className="text-gray-500 text-sm">Geospatial Satellite Map Integration Pending</p>
            <p className="text-xs text-gray-400 mt-1">(Requires Leaflet & GeoJSON polygons)</p>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">High Risk Zones</h3>
            <div className="text-3xl font-bold text-red-600">12%</div>
            <p className="text-sm text-gray-400 mt-1">of monitored area</p>
          </div>

          <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Water Stress Detected</h3>
            <div className="text-3xl font-bold text-amber-500">28%</div>
            <p className="text-sm text-gray-400 mt-1">of monitored area</p>
          </div>
        </div>
      </div>

      <h3 className="text-xl font-bold text-gray-800 pt-4">Recent Village Reports</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {mockInsights.map((insight, idx) => (
          <div key={idx} className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <h4 className="text-lg font-bold text-gray-800">{insight.village}</h4>
              <span className={`px-2.5 py-1 text-xs font-bold rounded-full uppercase ${
                insight.risk === 'high' ? 'bg-red-100 text-red-700' :
                insight.risk === 'medium' ? 'bg-amber-100 text-amber-700' :
                'bg-green-100 text-green-700'
              }`}>
                {insight.risk} Risk
              </span>
            </div>

            <div className="space-y-3 mb-4">
              <div className="flex items-center text-sm">
                <Activity className="w-4 h-4 mr-2 text-gray-400" />
                <span className="text-gray-600">NDVI Level: <span className="font-semibold text-gray-900">{insight.ndvi}</span></span>
              </div>
              <div className="flex items-center text-sm">
                <Droplets className="w-4 h-4 mr-2 text-gray-400" />
                <span className="text-gray-600">Water Stress:
                  <span className={`ml-1 font-semibold ${insight.waterStress ? 'text-red-600' : 'text-green-600'}`}>
                    {insight.waterStress ? 'Yes' : 'No'}
                  </span>
                </span>
              </div>
            </div>

            <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div className="flex items-start">
                <ShieldAlert className="w-4 h-4 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-gray-700 leading-snug">{insight.action}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
