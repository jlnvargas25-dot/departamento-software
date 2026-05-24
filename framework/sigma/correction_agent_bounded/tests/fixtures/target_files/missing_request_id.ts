import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  // No request ID extraction
  const body = await req.json();
  const result = await processOrder(body);
  return NextResponse.json(result);
}
