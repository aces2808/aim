# Agriyard Static Website - Dummy Content

This directory contains dummy HTML content for testing the S3 + CloudFront infrastructure.

## Files Included

- **`index.html`** - Main landing page with Agriyard branding and infrastructure status
- **`error.html`** - 404/error page that redirects to home (SPA support)
- **`styles.css`** - Basic CSS styles (optional external stylesheet)

## Features

### index.html

- ✅ Responsive design with mobile support
- ✅ Modern glassmorphism UI design
- ✅ Agriyard branding and information
- ✅ Infrastructure status display
- ✅ Technology stack showcase
- ✅ Interactive elements with JavaScript
- ✅ Performance optimized with inline CSS

### error.html

- ✅ Custom 404 error page
- ✅ Auto-redirect to home page
- ✅ SPA-friendly routing support
- ✅ Consistent branding

## Deployment

To deploy this content to your S3 bucket:

```bash
# Upload files to S3
aws s3 sync web-content/ s3://YOUR_BUCKET_NAME --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

## Testing

1. **Deploy Infrastructure**: First deploy the CDK stack
2. **Upload Content**: Use the commands above to upload these files
3. **Access Website**: Visit the CloudFront URL provided in stack outputs
4. **Test Error Handling**: Try accessing a non-existent path to test error.html

## Customization

- Update branding and content in `index.html`
- Modify styles in the `<style>` section or use external `styles.css`
- Add additional pages as needed
- Include favicon and other assets

## Production Notes

- Replace this dummy content with your actual React build
- Ensure proper cache headers for optimal performance
- Test all functionality before production deployment
- Monitor CloudFront metrics for performance optimization
