import { NextRequest } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL;
const API_SECRET = process.env.API_SECRET;

export async function POST(req: NextRequest) {
    const body = await req.json();

    const response = await fetch(`${BACKEND_URL}/chat`,{
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Internal-Token": API_SECRET!,
        },
        body: JSON.stringify(body),
    })

    // Reenviar el stream al browser
    return new Response(response.body, {
        headers:{
            "Content-Type": "text/plain",
            "Transfer-Encoding": "chunked"
        },
    });
}