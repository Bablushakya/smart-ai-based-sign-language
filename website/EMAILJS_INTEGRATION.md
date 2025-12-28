# EmailJS Integration - Contact Form

## ✅ Integration Complete!

Your contact form is now fully integrated with EmailJS and will send real emails.

## 📧 Configuration Details

### EmailJS Credentials Used:
- **Service ID**: `service_9hcjo9n`
- **Template ID**: `template_p0qw1qn`
- **Public Key**: `wwIyEjSN2vDFs2rYD`

### Form Field Mapping:
The form fields are mapped to EmailJS template variables as follows:

| Form Field | EmailJS Variable | Description |
|------------|------------------|-------------|
| `name` | `{{from_name}}` | Sender's full name |
| `email` | `{{from_email}}` | Sender's email address |
| `subject` | `{{subject}}` | Email subject line |
| `message` | `{{message}}` | Email message content |

## 🎯 How It Works

1. **User fills out the form** with their name, email, subject, and message
2. **User clicks "Send Message"** button
3. **Form validates** all required fields
4. **Button shows loading state** with spinner: "Sending..."
5. **EmailJS sends the email** to your configured email address
6. **Success modal appears** confirming the message was sent
7. **Form resets** automatically for next submission

## 🔧 Files Modified

### 1. `website/templates/contact.html`
Added EmailJS SDK and initialization:
```html
<!-- EmailJS SDK -->
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>
<script type="text/javascript">
    (function(){
        emailjs.init("wwIyEjSN2vDFs2rYD");
    })();
</script>
```

### 2. `website/static/js/contact.js`
Updated form submission handler to use EmailJS:
```javascript
emailjs.send('service_9hcjo9n', 'template_p0qw1qn', templateParams)
    .then(function(response) {
        // Success handling
    }, function(error) {
        // Error handling
    });
```

## ✨ Features

- ✅ **Real email sending** via EmailJS
- ✅ **Loading state** with spinner during send
- ✅ **Success modal** on successful send
- ✅ **Error handling** with user-friendly messages
- ✅ **Form validation** (all fields required)
- ✅ **Auto form reset** after successful send
- ✅ **No design changes** - all original styling preserved
- ✅ **3D video effects** still working
- ✅ **Animated background** still working

## 🧪 Testing

To test the contact form:

1. Go to your contact page
2. Fill in all fields:
   - Name: Your name
   - Email: Your email
   - Subject: Test message
   - Message: This is a test
3. Click "Send Message"
4. You should see:
   - Button changes to "Sending..." with spinner
   - Success modal appears
   - Form resets
   - Email arrives in your configured inbox

## 📊 EmailJS Dashboard

Monitor your emails at: https://dashboard.emailjs.com/admin

You can see:
- Number of emails sent
- Success/failure rates
- Email history
- Monthly quota usage

## 🔒 Security Notes

- **Public Key is safe** to expose in frontend code
- **Service ID and Template ID** are also safe to expose
- EmailJS handles rate limiting automatically
- Free tier: 200 emails/month
- Upgrade for more: https://www.emailjs.com/pricing/

## 🛠️ Troubleshooting

### Email not sending?
1. Check browser console for errors
2. Verify EmailJS credentials are correct
3. Check EmailJS dashboard for quota limits
4. Ensure email service is connected in EmailJS dashboard

### Wrong email template?
1. Go to https://dashboard.emailjs.com/admin/templates
2. Edit template `template_p0qw1qn`
3. Ensure variables match: `{{from_name}}`, `{{from_email}}`, `{{subject}}`, `{{message}}`

### Rate limiting?
- Free tier: 200 emails/month
- Upgrade at: https://www.emailjs.com/pricing/

## 📝 Email Template Example

Your EmailJS template should look like this:

```
Subject: New Contact Form Message: {{subject}}

From: {{from_name}}
Email: {{from_email}}

Message:
{{message}}

---
Sent from SignSpeak Contact Form
```

## 🎨 Design Preserved

All original design elements are preserved:
- ✅ Animated background with waves
- ✅ Floating particles
- ✅ Animated blobs with hand signs
- ✅ 3D video container with tilt effect
- ✅ Contact information cards
- ✅ Social links
- ✅ Success modal styling
- ✅ Form styling and animations

## 🚀 Next Steps

Your contact form is ready to use! No further configuration needed.

Optional enhancements you could add:
- Google reCAPTCHA for spam protection
- Custom success/error messages
- Email confirmation to sender
- Auto-reply functionality
- Form analytics tracking

## 📞 Support

If you need help:
- EmailJS Docs: https://www.emailjs.com/docs/
- EmailJS Support: https://www.emailjs.com/support/
