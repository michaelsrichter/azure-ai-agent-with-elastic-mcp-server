# DevTunnel Authentication Setup Guide

The devtunnel is currently configured to require authentication. Here are the solutions:

## Option 1: Configure Anonymous Access (Recommended for Development)

If you have access to the devtunnel configuration, you can allow anonymous access:

```bash
# Allow anonymous access to your tunnel
devtunnel access create [tunnel-id] --allow-anonymous

# Or when creating a new tunnel
devtunnel host -p 8080 --allow-anonymous
```

## Option 2: Create and Use Access Token

Create a tunnel access token and set it as an environment variable:

```bash
# Create a client access token for your tunnel
devtunnel token [tunnel-id] --scopes connect

# Copy the token and add it to your .env file
echo "DEVTUNNEL_ACCESS_TOKEN=your_token_here" >> .env
```

## Option 3: Use Different Authentication Method

Check your current tunnel status and permissions:

```bash
# List your tunnels
devtunnel list

# Show tunnel details including access permissions
devtunnel show [tunnel-id]

# Show current user info
devtunnel user show
```

## Current Issue

The authentication error suggests that:
1. The tunnel requires authentication with the same Microsoft account that created it
2. Our current Azure AD token approach isn't working with this specific tunnel
3. The tunnel might not be configured for the authentication method we're using

## Quick Test

You can test if the issue is with our authentication by temporarily configuring anonymous access:

```bash
devtunnel access create [tunnel-id] --allow-anonymous
```

Then test the connection again. If it works, we know the issue was authentication-related.

## Next Steps

1. Check if you can modify the tunnel configuration
2. If yes, enable anonymous access for development
3. If no, create an access token and add it to the .env file
4. Alternative: Set up a new tunnel with appropriate permissions

Let me know which approach you'd like to take!
