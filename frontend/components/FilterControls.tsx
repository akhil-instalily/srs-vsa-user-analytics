"use client";

import { ProductContext, UserType } from "@/lib/types";
import { RotateCcw } from "lucide-react";

interface FilterControlsProps {
  startDate: string;
  endDate: string;
  productContext: ProductContext;
  userType: UserType;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
  onProductContextChange: (context: ProductContext) => void;
  onUserTypeChange: (type: UserType) => void;
  onReset: () => void;
}

export function FilterControls({
  startDate,
  endDate,
  productContext,
  userType,
  onStartDateChange,
  onEndDateChange,
  onProductContextChange,
  onUserTypeChange,
  onReset,
}: FilterControlsProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm mb-6">
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Start Date
          </label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => onStartDateChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            End Date
          </label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => onEndDateChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Product Context
          </label>
          <select
            value={productContext}
            onChange={(e) =>
              onProductContextChange(e.target.value as ProductContext)
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
          >
            <option value="pool">Heritage Pool Plus</option>
            <option value="landscape">Heritage Plus</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            User Type
          </label>
          <select
            value={userType}
            onChange={(e) => onUserTypeChange(e.target.value as UserType)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
          >
            <option value="all">All Users</option>
            <option value="internal">Internal Users</option>
            <option value="external">External Users</option>
          </select>
        </div>

        <div className="flex items-end">
          <button
            onClick={onReset}
            className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Reset Filters
          </button>
        </div>
      </div>
    </div>
  );
}
