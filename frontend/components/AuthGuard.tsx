"use client";

import { useAuth0 } from "@auth0/auth0-react";
import { Loader2 } from "lucide-react";

// Only these email domains are allowed access
const ALLOWED_DOMAINS = [
  "srsdistribution.com",
  "instalily.ai",
  "mmhfgb.com",
  "heritagelsg.com",
  "heritagepsg.com",
];

interface AuthGuardProps {
  children: React.ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const { isAuthenticated, isLoading, user, loginWithRedirect, logout } = useAuth0();

  // Show loading state while Auth0 initializes
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If not authenticated, redirect to Auth0 login
  if (!isAuthenticated) {
    loginWithRedirect();
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  // Check if user's email domain is allowed
  if (user && user.email) {
    const emailDomain = user.email.split("@")[1]?.toLowerCase();
    const isAllowed = ALLOWED_DOMAINS.some(
      (domain) => emailDomain === domain.toLowerCase()
    );

    if (!isAllowed) {
      // Log out unauthorized users
      logout({ logoutParams: { returnTo: window.location.origin } });
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="bg-red-50 border border-red-200 rounded-lg p-8 max-w-md text-center">
            <h2 className="text-xl font-bold text-red-800 mb-2">Access Denied</h2>
            <p className="text-red-600 mb-4">
              Your email domain is not authorized to access this application.
            </p>
            <p className="text-sm text-gray-600">
              Allowed domains: {ALLOWED_DOMAINS.join(", ")}
            </p>
          </div>
        </div>
      );
    }
  }

  // User is authenticated and authorized
  return <>{children}</>;
}
