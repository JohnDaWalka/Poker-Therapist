# Vercel Deployment Guide for Poker Therapist

This guide explains how to deploy the Poker Therapist application to Vercel.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed (optional, for command-line deployment)
3. Required API keys:
   - xAI API key
   - OpenAI API key
   - Anthropic API key (optional)
   - Google API key (optional)

## Deployment Options

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Connect Repository**
   - Go to https://vercel.com/new
   - Import the `JohnDaWalka/Poker-Therapist` repository
   - Vercel will automatically detect the `vercel.json` configuration

2. **Configure Environment Variables**
   Add the following environment variables in the Vercel dashboard:
   - `XAI_API_KEY`: Your xAI API key
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ANTHROPIC_API_KEY`: Your Anthropic API key (optional)
   - `GOOGLE_API_KEY`: Your Google API key (optional)
   - `AUTHORIZED_EMAILS`: Comma-separated list of authorized user emails

3. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your application
   - Your app will be available at `https://poker-therapist.vercel.app` (or your custom domain)

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from Project Root**
   ```bash
   cd /path/to/Poker-Therapist
   vercel
   ```

4. **Set Environment Variables**
   ```bash
   vercel env add XAI_API_KEY
   vercel env add OPENAI_API_KEY
   vercel env add ANTHROPIC_API_KEY
   vercel env add GOOGLE_API_KEY
   vercel env add AUTHORIZED_EMAILS
   ```

5. **Deploy to Production**
   ```bash
   vercel --prod
   ```

## Configuration Files

### vercel.json
The main configuration file that defines:
- Build settings
- Routes and redirects
- Environment variable references
- Serverless function configuration

### .vercelignore
Specifies files and directories to exclude from deployment:
- Test files
- Documentation
- Development dependencies
- Database files
- IDE configuration

### api/index.py
The serverless function entrypoint that wraps the FastAPI application for Vercel.

## API Endpoints

After deployment, your API will be available at:
- Health check: `https://your-app.vercel.app/health`
- API docs: `https://your-app.vercel.app/docs`
- Root: `https://your-app.vercel.app/`

### Available Routes
- `/api/triage` - Triage endpoints
- `/api/deep-session` - Deep session endpoints
- `/api/analyze` - Analysis endpoints
- `/api/tracking` - Tracking endpoints

## CORS Configuration

The FastAPI application is pre-configured to allow requests from:
- `http://localhost:3000` (local development)
- `http://localhost:8080` (local development)
- `http://localhost:5173` (local development)
- `https://*.vercel.app` (Vercel preview deployments)
- `https://poker-therapist.vercel.app` (production)

## Limitations

### Vercel Serverless Functions
- Maximum execution time: 10 seconds (Hobby), 60 seconds (Pro)
- Maximum payload size: 4.5 MB
- Maximum Lambda size: 50 MB (configured in vercel.json)

### Not Supported on Vercel
- Long-running processes
- WebSocket connections (for real-time voice streaming)
- File system persistence (use external storage)

### Workarounds
For features that require long-running processes or WebSockets:
1. Use Vercel for the API backend
2. Deploy Streamlit app separately (e.g., Streamlit Cloud, Railway, Render)
3. Use external services for real-time features

## Monitoring and Logs

1. **View Logs**
   - Go to your Vercel dashboard
   - Select your project
   - Navigate to the "Logs" tab

2. **Monitor Performance**
   - View function invocations
   - Check response times
   - Monitor error rates

## Custom Domain

To use a custom domain:
1. Go to your project settings in Vercel
2. Navigate to "Domains"
3. Add your custom domain
4. Update DNS records as instructed

## Troubleshooting

### Build Fails
- Check that all dependencies are listed in `requirements.txt`
- Verify that Python version is compatible (3.12+)
- Check build logs in Vercel dashboard

### Import Errors
- Ensure all modules are properly imported in `api/index.py`
- Verify that the project structure is correct
- Check that all required files are not in `.vercelignore`

### Environment Variables Not Working
- Verify variables are set in Vercel dashboard
- Check variable names match those in the code
- Redeploy after adding/updating variables

### CORS Issues
- Verify allowed origins in `backend/api/main.py`
- Check that requests include proper headers
- Test with different origins

## Updates and Redeployment

Vercel automatically redeploys when you push to your connected Git repository:
1. Push changes to your repository
2. Vercel detects the change
3. Automatic build and deployment starts
4. New version goes live

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/runtimes#official-runtimes/python)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

## Support

For issues specific to Vercel deployment:
- Check Vercel [Status Page](https://www.vercel-status.com/)
- Visit [Vercel Community](https://github.com/vercel/vercel/discussions)
- Review [Vercel Examples](https://github.com/vercel/examples)

For application-specific issues:
- Check the main README.md
- Review DEPLOYMENT_CHECKLIST.md
- Open an issue on GitHub
