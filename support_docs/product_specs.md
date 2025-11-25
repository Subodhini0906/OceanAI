# Product Specifications - E-Shop Checkout

## Discount Codes

### Valid Discount Codes
- **SAVE15**: Applies a 15% discount to the total order amount (excluding shipping)
- Discount codes are case-sensitive
- Only one discount code can be applied per order
- Discount codes cannot be combined

### Discount Application Rules
- Discount is applied to the subtotal (sum of all items in cart)
- Shipping costs are NOT discounted
- Discount must be applied before final payment
- Invalid discount codes will show an error message

## Shipping Options

### Standard Shipping
- **Cost**: Free ($0.00)
- **Delivery Time**: 5-7 business days
- Default shipping method

### Express Shipping
- **Cost**: $10.00
- **Delivery Time**: 2-3 business days
- Additional fee added to order total

## Cart Functionality

### Add to Cart
- Users can add multiple items to cart
- Each item can be added multiple times
- Cart persists during the checkout session

### Quantity Management
- Users can modify item quantities in the cart summary
- Minimum quantity is 1
- If quantity is set to 0, item is removed from cart

### Cart Summary
- Displays all items with individual prices
- Shows subtotal (sum of all items)
- Shows shipping cost
- Shows final total (subtotal + shipping - discount)

## Payment Methods

### Credit Card
- Standard payment method
- Requires valid card details (not implemented in UI)
- Default payment option

### PayPal
- Alternative payment method
- Requires PayPal account (not implemented in UI)

## Form Validation

### Required Fields
- **Name**: Must not be empty
- **Email**: Must be a valid email format (contains @ and domain)
- **Address**: Must not be empty

### Validation Behavior
- Error messages appear in red text below invalid fields
- Errors are shown on field blur (when user leaves the field)
- Errors are also validated on form submission
- Form cannot be submitted until all validations pass

### Email Validation Rules
- Must contain @ symbol
- Must have characters before @
- Must have domain after @
- Must have top-level domain (e.g., .com, .org)

## Payment Processing

### Payment Success
- "Pay Now" button triggers payment processing
- Payment is only processed if:
  - All form fields are valid
  - Cart contains at least one item
- Upon successful payment, displays "Payment Successful!" message
- Form is hidden after successful payment

### Payment Button
- Button is disabled after successful payment
- Button text: "Pay Now"
- Button is green in color

