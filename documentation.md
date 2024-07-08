# Frontend Developer Instructions
# Update User

## Endpoint
`PUT http://localhost:5000/api/officers/6`

## Request Body
```json
{
    "officer_name": "Induwara",
    "officer_grade": "A",
    "officer_nic": "01234569",
    "officer_username": "leo",
    "officer_email": "ashen1.doe@example.com",
    "officer_password": "Lakindu123!@",
    "officer_phone_number": "0123456789",
    "officer_position": "Manager",
    "officer_role": "Admin",
    "officer_power_level": 5,
    "committee": true
}
```

# User Login
## Storing Token After Login in FrontEnd

To store the token after a successful login, use the following code:

```javascript
async function login() {
    const response = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: 'test',
            password: 'password',
        }),
    });
    
    const data = await response.json();
    if (response.ok) {
        localStorage.setItem('token', data.token);
        window.location.href = '/dashboard';
    } else {
        alert(data.message);
    }
}
```

