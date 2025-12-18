import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const baseTime = searchParams.get('baseTime')
  const validTime = searchParams.get('validTime')
  const variable = searchParams.get('variable')

  // Here you would typically make a request to your FastAPI backend
  // For now, we'll return mock data
  // TODO: migrate to use the backend api when we need middlewares and authentications
  const mockData = {
    baseTime,
    validTime,
    variable,
    data: [
      { lat: 40.7128, lon: -74.0060, value: 72 },
      { lat: 34.0522, lon: -118.2437, value: 85 },
      { lat: 41.8781, lon: -87.6298, value: 68 },
    ]
  }

  return NextResponse.json(mockData)
}
