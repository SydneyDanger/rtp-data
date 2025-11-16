/**
 * Cloudflare Worker: Simple CORS Proxy for SlotCatalog Scraping
 * 
 * Deploy this to Cloudflare Workers to bypass CORS restrictions
 * Usage: https://your-worker.workers.dev/?url=https://slotcatalog.com/en/slots/game-name
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Get the target URL from query parameter
  const url = new URL(request.url)
  const targetUrl = url.searchParams.get('url')
  
  // Validate target URL
  if (!targetUrl) {
    return new Response('Missing url parameter', { status: 400 })
  }
  
  // Only allow SlotCatalog URLs (security measure)
  if (!targetUrl.startsWith('https://slotcatalog.com/')) {
    return new Response('Only SlotCatalog URLs are allowed', { status: 403 })
  }
  
  try {
    // Fetch the target URL
    const response = await fetch(targetUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
      }
    })
    
    // Get the response body
    const body = await response.text()
    
    // Return with CORS headers
    return new Response(body, {
      status: response.status,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
      }
    })
    
  } catch (error) {
    return new Response(`Error fetching URL: ${error.message}`, { 
      status: 500,
      headers: {
        'Access-Control-Allow-Origin': '*',
      }
    })
  }
}
