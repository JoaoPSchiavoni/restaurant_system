import express from 'express';
import morgan from 'morgan';
import cors from 'cors';

const app = express();
const PORT = process.env.PORT || 3000;
const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

app.use(cors());
app.use(morgan('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static UI assets
app.use(express.static('public'));

// Proxy route handler for auth and order APIs
app.use(['/auth', '/order'], async (req, res) => {
  const targetUrl = `${FASTAPI_URL}${req.originalUrl}`;
  console.log(`[Proxy] Routing ${req.method} ${req.originalUrl} -> ${targetUrl}`);

  try {
    const headers = {};
    if (req.headers.authorization) {
      headers['authorization'] = req.headers.authorization;
    }

    const options = {
      method: req.method,
      headers: headers
    };

    if (req.method !== 'GET' && req.method !== 'HEAD') {
      const contentType = req.headers['content-type'] || 'application/json';
      
      if (contentType.includes('application/json')) {
        options.headers['content-type'] = 'application/json';
        options.body = JSON.stringify(req.body);
      } else if (contentType.includes('application/x-www-form-urlencoded')) {
        options.headers['content-type'] = 'application/x-www-form-urlencoded';
        const params = new URLSearchParams();
        for (const [key, value] of Object.entries(req.body)) {
          params.append(key, value);
        }
        options.body = params.toString();
      } else {
        options.headers['content-type'] = contentType;
        options.body = req.body;
      }
    }

    const apiResponse = await fetch(targetUrl, options);
    const resContentType = apiResponse.headers.get('content-type');
    
    if (resContentType) {
      res.setHeader('content-type', resContentType);
    }
    
    res.status(apiResponse.status);

    if (resContentType && resContentType.includes('application/json')) {
      const data = await apiResponse.json();
      res.json(data);
    } else {
      const text = await apiResponse.text();
      res.send(text);
    }
  } catch (error) {
    console.error(`[Proxy Error] Failed to connect to ${targetUrl}:`, error.message);
    res.status(502).json({
      detail: `Backend service is offline. Please make sure the FastAPI backend is running on ${FASTAPI_URL}.`
    });
  }
});

app.listen(PORT, () => {
  console.log(`==================================================`);
  console.log(`Restaurant System Web Server running at:`);
  console.log(`👉 http://localhost:${PORT}`);
  console.log(`Proxying requests to FastAPI backend at:`);
  console.log(`👉 ${FASTAPI_URL}`);
  console.log(`==================================================`);
});
