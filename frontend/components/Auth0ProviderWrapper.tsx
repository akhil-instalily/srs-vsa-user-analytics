"use client";

import { Auth0Provider } from "@auth0/auth0-react";

interface Auth0ProviderWrapperProps {
  children: React.ReactNode;
}

export function Auth0ProviderWrapper({ children }: Auth0ProviderWrapperProps) {
  return (
    <Auth0Provider
      domain="instalily.us.auth0.com"
      clientId="j5OMoC5Za1fOOatuFkmYnwCLLOAC8noS"
      cacheLocation="localstorage"
      authorizationParams={{
        redirect_uri: typeof window !== "undefined" ? window.location.origin : "",
        audience: "https://instalily.us.auth0.com/api/v2/",
      }}
    >
      {children}
    </Auth0Provider>
  );
}
