"use client";

import { useState, useEffect } from "react";
import { format } from "date-fns";
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import {
  MessageSquare,
  Users,
  TrendingUp,
  Clock,
  ThumbsUp,
  ThumbsDown,
  Loader2,
} from "lucide-react";
import { FilterControls } from "@/components/FilterControls";
import { StatCard } from "@/components/StatCard";
import { fetchAllFastKPIs, fetchPainPointClustering, fetchSentimentAnalysis } from "@/lib/api";
import type {
  AnalyticsFilters,
  DashboardData,
  ProductContext,
  UserType,
} from "@/lib/types";

const COLORS = [
  "#3b82f6", // blue
  "#10b981", // green
  "#f59e0b", // amber
  "#ef4444", // red
  "#8b5cf6", // purple
  "#ec4899", // pink
  "#14b8a6", // teal
];

// Helper function to format category names
function formatCategoryName(name: string): string {
  return name
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export default function Home() {
  // Default to December 2025
  const [startDate, setStartDate] = useState("2025-12-01");
  const [endDate, setEndDate] = useState("2025-12-31");
  const [productContext, setProductContext] = useState<ProductContext>("pool");
  const [userType, setUserType] = useState<UserType>("all");

  const [data, setData] = useState<DashboardData | null>(null);
  const [clustering, setClustering] = useState<any>(null);
  const [sentiment, setSentiment] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [clusteringLoading, setClusteringLoading] = useState(true);
  const [sentimentLoading, setSentimentLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch data when filters change
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setClusteringLoading(true);
      setSentimentLoading(true);
      setError(null);

      const filters: AnalyticsFilters = {
        startDate: `${startDate}T00:00:00`,
        endDate: `${endDate}T23:59:59`,
        productContext,
        userType,
      };

      try {
        // Fetch fast KPIs immediately
        const fastData = await fetchAllFastKPIs(filters);
        setData({
          ...fastData,
          painPointClustering: null,
          sentimentAnalysis: null,
        });
        setLoading(false);

        // Fetch slow clustering and sentiment separately
        const clusteringData = await fetchPainPointClustering(filters);
        setClustering(clusteringData);
        setClusteringLoading(false);

        const sentimentData = await fetchSentimentAnalysis(filters);
        setSentiment(sentimentData);
        setSentimentLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch data");
        setLoading(false);
        setClusteringLoading(false);
        setSentimentLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, productContext, userType]);

  const handleReset = () => {
    setStartDate("2025-12-01");
    setEndDate("2025-12-31");
    setProductContext("pool");
    setUserType("all");
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h3 className="text-red-800 font-semibold mb-2">Error</h3>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            VSA User Analytics Dashboard
          </h1>
          <p className="text-gray-600 mt-1">
            Virtual Shopping Assistant analytics for Heritage Plus and Heritage Pool Plus
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Filters */}
        <FilterControls
          startDate={startDate}
          endDate={endDate}
          productContext={productContext}
          userType={userType}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
          onProductContextChange={setProductContext}
          onUserTypeChange={setUserType}
          onReset={handleReset}
        />

        {/* Top Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Sessions"
            value={data.sessionMetrics?.total_sessions || 0}
            icon={MessageSquare}
            iconColor="text-blue-500"
          />
          <StatCard
            title="Unique Users"
            value={data.userEngagement?.unique_users || 0}
            subtitle={`${(data.userEngagement?.avg_conversations_per_user || 0).toFixed(1)} avg conversations/user`}
            icon={Users}
            iconColor="text-green-500"
          />
          <StatCard
            title="Positive Feedback"
            value={data.sessionMetrics?.positive_feedback_sessions || 0}
            subtitle={`${data.sessionMetrics?.negative_feedback_sessions || 0} negative`}
            icon={ThumbsUp}
            iconColor="text-emerald-500"
          />
          <StatCard
            title="Avg Response Time"
            value={`${(data.sessionMetrics?.avg_response_time || 0).toFixed(1)}s`}
            icon={Clock}
            iconColor="text-purple-500"
          />
        </div>

        {/* Volume Trends Chart */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            Session Volume Trends
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.volumeTrends?.daily_data || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={(date) => format(new Date(date), "MMM dd")}
              />
              <YAxis />
              <Tooltip
                labelFormatter={(date) => format(new Date(date), "MMM dd, yyyy")}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="session_count"
                stroke="#3b82f6"
                strokeWidth={2}
                name="Sessions"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Query Categories Pie Chart */}
          <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900 mb-6">
              Query Categories
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={data.queryCategories?.categories || [] as any}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry: any) => `${formatCategoryName(entry.category)}: ${entry.percentage}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="session_count"
                >
                  {(data.queryCategories?.categories || []).map((_, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Pain Point Clustering */}
          <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900 mb-6">
              Pain Point Clustering
            </h2>
            {clusteringLoading ? (
              <div className="flex items-center justify-center h-[300px]">
                <div className="text-center">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">
                    Analyzing queries... This may take a few minutes
                  </p>
                </div>
              </div>
            ) : clustering ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={clustering.clusters as any}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry: any) => `${entry.percentage}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="count"
                    nameKey="cluster_name"
                  >
                    {clustering.clusters.map((_: any, index: number) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend
                    wrapperStyle={{ fontSize: "12px" }}
                    formatter={(value) => value.split(" – ")[0]}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-12">
                No clustering data available
              </p>
            )}
          </div>
        </div>

        {/* User Segmentation */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            User Segmentation
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.userSegmentation?.segments || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="segment_name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="user_count" fill="#3b82f6" name="Users" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Additional Metrics Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* User Retention */}
          <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              User Retention
            </h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Retention Rate</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(data.userRetention?.returning_users_percentage || 0).toFixed(1)}%
                </p>
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-600">Returning Users</p>
                <p className="text-xl font-semibold text-gray-900">
                  {data.userRetention?.returning_users || 0}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">One-time Users</p>
                <p className="text-xl font-semibold text-gray-900">
                  {data.userRetention?.one_time_users || 0}
                </p>
              </div>
            </div>
          </div>

          {/* Conversation Length */}
          <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Conversation Length
            </h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Average Messages</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(data.conversationLength?.avg_messages_per_session || 0).toFixed(1)}
                </p>
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-600">Total Sessions</p>
                <p className="text-xl font-semibold text-gray-900">
                  {data.conversationLength?.total_sessions || 0}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Longest Conversation</p>
                <p className="text-xl font-semibold text-gray-900">
                  {data.conversationLength?.longest_session_messages || 0} messages
                </p>
              </div>
            </div>
          </div>

          {/* Returning User Behavior */}
          <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Returning User Behavior
            </h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Avg Sessions/User</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(data.returningUserBehavior?.avg_sessions_per_returning_user || 0).toFixed(
                    1
                  )}
                </p>
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-600">Avg Active Days</p>
                <p className="text-xl font-semibold text-gray-900">
                  {(data.returningUserBehavior?.avg_days_between_first_last || 0).toFixed(1)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Returning Users</p>
                <p className="text-xl font-semibold text-gray-900">
                  {data.returningUserBehavior?.returning_users_count || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Time Patterns */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            Usage by Hour of Day
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.timePatterns?.by_hour || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" tickFormatter={(h) => `${h}:00`} />
              <YAxis />
              <Tooltip labelFormatter={(h) => `${h}:00`} />
              <Bar dataKey="session_count" fill="#3b82f6" name="Sessions" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Sentiment Analysis */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            Sentiment Analysis
          </h2>
          {sentimentLoading ? (
            <div className="flex items-center justify-center h-[400px]">
              <div className="text-center">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-2" />
                <p className="text-sm text-gray-500">
                  Analyzing message sentiment...
                </p>
              </div>
            </div>
          ) : sentiment ? (
            <div className="space-y-6">
              {/* Sentiment Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-sm text-blue-600 font-medium">Total Messages</p>
                  <p className="text-2xl font-bold text-blue-900">{sentiment.total_messages}</p>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <p className="text-sm text-purple-600 font-medium">Average Score</p>
                  <p className="text-2xl font-bold text-purple-900">{sentiment.avg_sentiment_score.toFixed(3)}</p>
                  <p className="text-xs text-purple-600 mt-1">Scale: -1 (negative) to +1 (positive)</p>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-sm text-green-600 font-medium">Sentiment Trend</p>
                  <p className="text-2xl font-bold text-green-900">
                    {sentiment.avg_sentiment_score > 0.05 ? "Positive" : sentiment.avg_sentiment_score < -0.05 ? "Negative" : "Neutral"}
                  </p>
                </div>
              </div>

              {/* Distribution Chart */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribution</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={sentiment.sentiment_distribution as any}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={(entry: any) => `${entry.category}: ${entry.percentage}%`}
                        outerRadius={90}
                        fill="#8884d8"
                        dataKey="count"
                      >
                        {sentiment.sentiment_distribution.map((_: any, index: number) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={index === 0 ? "#10b981" : index === 1 ? "#6b7280" : "#ef4444"}
                          />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Breakdown</h3>
                  <div className="space-y-3">
                    {sentiment.sentiment_distribution.map((cat: any) => (
                      <div key={cat.category} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                        <div className="flex items-center gap-2">
                          <div className={`w-3 h-3 rounded-full ${
                            cat.category === "positive" ? "bg-green-500" :
                            cat.category === "neutral" ? "bg-gray-500" : "bg-red-500"
                          }`}></div>
                          <span className="font-medium capitalize">{cat.category}</span>
                        </div>
                        <div className="text-right">
                          <p className="font-bold">{cat.count}</p>
                          <p className="text-sm text-gray-600">{cat.percentage}%</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Most Positive/Negative Messages */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-green-900 mb-3 flex items-center gap-2">
                    <ThumbsUp className="w-5 h-5" />
                    Most Positive Messages
                  </h3>
                  <div className="space-y-2">
                    {sentiment.most_positive_messages.slice(0, 3).map((msg: any, idx: number) => (
                      <div key={idx} className="p-3 bg-green-50 rounded border border-green-200">
                        <p className="text-sm text-gray-800 mb-1">{msg.message}</p>
                        <p className="text-xs font-semibold text-green-700">Score: {msg.score.toFixed(3)}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-red-900 mb-3 flex items-center gap-2">
                    <ThumbsDown className="w-5 h-5" />
                    Most Negative Messages
                  </h3>
                  <div className="space-y-2">
                    {sentiment.most_negative_messages.slice(0, 3).map((msg: any, idx: number) => (
                      <div key={idx} className="p-3 bg-red-50 rounded border border-red-200">
                        <p className="text-sm text-gray-800 mb-1">{msg.message}</p>
                        <p className="text-xs font-semibold text-red-700">Score: {msg.score.toFixed(3)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-12">
              No sentiment data available
            </p>
          )}
        </div>

        {/* Clustering Details Table */}
        {clustering && !clusteringLoading && (
          <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900 mb-6">
              Pain Point Details
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                      Cluster
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                      Count
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                      Percentage
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                      Example Queries
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {clustering.clusters.map((cluster: any) => (
                    <tr
                      key={cluster.cluster_id}
                      className="border-b border-gray-100 hover:bg-gray-50"
                    >
                      <td className="py-3 px-4 text-sm text-gray-900">
                        {cluster.cluster_name}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-900">
                        {cluster.count}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-900">
                        {cluster.percentage}%
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {cluster.example_queries.slice(0, 3).join("; ")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
