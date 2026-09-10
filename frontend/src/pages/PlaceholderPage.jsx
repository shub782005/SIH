import React from 'react';
import { Construction } from 'lucide-react';

export default function PlaceholderPage({ title, description }) {
  return (
    <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center space-y-4 max-w-xl mx-auto my-12 shadow-sm">
      <div className="w-12 h-12 bg-amber-50 rounded-2xl flex items-center justify-center mx-auto text-amber-600 border border-amber-200">
        <Construction className="w-6 h-6" />
      </div>
      <div>
        <span className="text-xs font-semibold text-amber-600 bg-amber-100 px-2.5 py-1 rounded-full uppercase tracking-wide">
          Coming Soon
        </span>
        <h2 className="text-xl font-bold text-slate-800 mt-2">{title}</h2>
        <p className="text-slate-500 text-xs mt-1 max-w-md mx-auto">{description}</p>
      </div>
    </div>
  );
}
