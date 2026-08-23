// Netlify Serverless Function for Real-Time Multi-Device Sync
let memoryStore = {};

exports.handler = async (event, context) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: 'OK' };
    }

    if (event.httpMethod === 'POST') {
        try {
            const body = JSON.parse(event.body);
            if (body && body.namespace) {
                memoryStore[body.namespace] = {
                    data: body,
                    updated_at: Date.now()
                };
            }
            return {
                statusCode: 200,
                headers,
                body: JSON.stringify({ success: true, updated_at: Date.now() })
            };
        } catch(e) {
            return { statusCode: 400, headers, body: JSON.stringify({ error: e.message }) };
        }
    }

    if (event.httpMethod === 'GET') {
        const ns = event.queryStringParameters.namespace || 'SPS_ACCOUNT_V1_';
        const record = memoryStore[ns] || null;
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({ data: record ? record.data : null })
        };
    }

    return { statusCode: 405, headers, body: 'Method Not Allowed' };
};
