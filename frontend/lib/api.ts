import type {
  AnalyticsFilters,
  SessionMetrics,
  PainPointClustering,
  VolumeTrends,
  UserEngagement,
  UserRetention,
  QueryCategories,
  ReturningUserBehavior,
  UserSegmentation,
  TimePatterns,
  ConversationLength,
  PlatformAnalytics,
  SentimentAnalysis,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

// Token storage for authenticated API calls
let authToken: string | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
}

function getAuthHeaders(): HeadersInit {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  return headers;
}

function buildQueryString(filters: AnalyticsFilters): string {
  const params = new URLSearchParams({
    start_date: filters.startDate,
    end_date: filters.endDate,
    product_context: filters.productContext,
    user_type: filters.userType,
  });

  if (filters.environment) {
    params.append("environment", filters.environment);
  }

  if (filters.userId) {
    params.append("user_id", filters.userId);
  }

  return params.toString();
}

export async function fetchSessionMetrics(
  filters: AnalyticsFilters
): Promise<SessionMetrics> {
  const response = await fetch(
    `${API_URL}/analytics/session-metrics?${buildQueryString(filters)}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) throw new Error("Failed to fetch session metrics");
  return response.json();
}

export async function fetchPainPointClustering(
  filters: AnalyticsFilters
): Promise<PainPointClustering> {
  const response = await fetch(
    `${API_URL}/analytics/pain-point-clustering?${buildQueryString(filters)}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) throw new Error("Failed to fetch pain point clustering");
  return response.json();
}

export async function fetchVolumeTrends(
  filters: AnalyticsFilters
): Promise<VolumeTrends> {
  const response = await fetch(
    `${API_URL}/analytics/volume-trends?${buildQueryString(filters)}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) throw new Error("Failed to fetch volume trends");
  return response.json();
}

export async function fetchUserEngagement(
  filters: AnalyticsFilters
): Promise<UserEngagement> {
  const response = await fetch(
    `${API_URL}/analytics/user-engagement?${buildQueryString(filters)}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) throw new Error("Failed to fetch user engagement");
  return response.json();
}

export async function fetchUserRetention(
  filters: AnalyticsFilters
): Promise<UserRetention> {
  const response = await fetch(
    `${API_URL}/analytics/user-retention?${buildQueryString(filters)}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) throw new Error("Failed to fetch user retention");
  return response.json();
}

export async function fetchQueryCategories(
  filters: AnalyticsFilters
): Promise<QueryCategories> {
  const response = await fetch(
    `${API_URL}/analytics/query-categories?${buildQueryString(filters)}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) throw new Error("Failed to fetch query categories");
  return response.json();
}

export async function fetchReturningUserBehavior(
  filters: AnalyticsFilters
): Promise<ReturningUserBehavior> {
  const response = await fetch(
    `${API_URL}/analytics/returning-user-behavior?${buildQueryString(filters)}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) throw new Error("Failed to fetch returning user behavior");
  return response.json();
}

export async function fetchUserSegmentation(
  filters: AnalyticsFilters
): Promise<UserSegmentation> {
  const response = await fetch(
    `${API_URL}/analytics/user-segmentation?${buildQueryString(filters)}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) throw new Error("Failed to fetch user segmentation");
  return response.json();
}

export async function fetchTimePatterns(
  filters: AnalyticsFilters
): Promise<TimePatterns> {
  const response = await fetch(
    `${API_URL}/analytics/time-patterns?${buildQueryString(filters)}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) throw new Error("Failed to fetch time patterns");
  return response.json();
}

export async function fetchConversationLength(
  filters: AnalyticsFilters
): Promise<ConversationLength> {
  const response = await fetch(
    `${API_URL}/analytics/conversation-length?${buildQueryString(filters)}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) throw new Error("Failed to fetch conversation length");
  return response.json();
}

export async function fetchPlatformAnalytics(
  filters: AnalyticsFilters
): Promise<PlatformAnalytics> {
  const response = await fetch(
    `${API_URL}/analytics/platform-analytics?${buildQueryString(filters)}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) throw new Error("Failed to fetch platform analytics");
  return response.json();
}

export async function fetchSentimentAnalysis(
  filters: AnalyticsFilters
): Promise<SentimentAnalysis> {
  const response = await fetch(
    `${API_URL}/analytics/sentiment-analysis?${buildQueryString(filters)}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) throw new Error("Failed to fetch sentiment analysis");
  return response.json();
}

// Fetch all fast KPIs in parallel
export async function fetchAllFastKPIs(filters: AnalyticsFilters) {
  const [
    sessionMetrics,
    volumeTrends,
    userEngagement,
    userRetention,
    queryCategories,
    returningUserBehavior,
    userSegmentation,
    timePatterns,
    conversationLength,
    platformAnalytics,
  ] = await Promise.all([
    fetchSessionMetrics(filters),
    fetchVolumeTrends(filters),
    fetchUserEngagement(filters),
    fetchUserRetention(filters),
    fetchQueryCategories(filters),
    fetchReturningUserBehavior(filters),
    fetchUserSegmentation(filters),
    fetchTimePatterns(filters),
    fetchConversationLength(filters),
    fetchPlatformAnalytics(filters),
  ]);

  return {
    sessionMetrics,
    volumeTrends,
    userEngagement,
    userRetention,
    queryCategories,
    returningUserBehavior,
    userSegmentation,
    timePatterns,
    conversationLength,
    platformAnalytics,
  };
}
