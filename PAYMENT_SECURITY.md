# 🔒 Payment Security & Access Control - Perspective UPSC

## Critical Security Fixes Implemented

### 🚨 Security Issues Identified & Fixed:

**Problem:**
Students could potentially access test solutions and download PDFs without completing payment by:
1. Initiating payment (creating a pending purchase)
2. Closing payment window
3. Attempting to access solutions/PDFs

**Solution:**
Implemented strict payment verification checks across ALL access points.

---

## 🛡️ Payment Verification Flow

### Step-by-Step Process:

```
1. Student clicks "Purchase Test" or "Checkout Cart"
   ↓
2. Backend creates Purchase record with status="pending"
   ↓
3. Razorpay order created
   ↓
4. Student redirected to Razorpay payment page
   ↓
5. Student completes payment
   ↓
6. Razorpay sends payment details back
   ↓
7. Frontend calls /verify-payment or /cart/verify-payment
   ↓
8. Backend verifies Razorpay signature (cryptographic verification)
   ↓
9. If valid: Purchase status updated to "completed"
   ↓
10. Only NOW student can access test, solutions, and PDF
```

---

## 🔐 Security Checkpoints

### Checkpoint 1: Test Access (`/tests/{test_id}/take`)
**Requirements:**
- ✅ Valid JWT token (student must be logged in)
- ✅ Purchase record exists
- ✅ Purchase status = "completed" ← **CRITICAL**
- ✅ Test not already taken

**Code:**
```python
purchase = await db.purchases.find_one({
    "student_id": current_user.id,
    "test_id": test_id,
    "status": "completed"  # Payment verified
})
if not purchase:
    raise HTTPException(status_code=403, detail="Test not purchased")
```

### Checkpoint 2: View Solutions (`/test-solutions/{test_id}`)
**Requirements:**
- ✅ Valid JWT token
- ✅ Purchase status = "completed" ← **NEWLY ADDED**
- ✅ Test must be completed

**Code:**
```python
# CRITICAL: Check payment status
purchase = await db.purchases.find_one({
    "student_id": current_user.id,
    "test_id": test_id,
    "status": "completed"  # MUST be completed payment
})
if not purchase:
    raise HTTPException(
        status_code=403,
        detail="You must complete the payment before viewing solutions"
    )

# Then check test completion
result = await db.test_results.find_one({
    "student_id": current_user.id,
    "test_id": test_id
})
if not result:
    raise HTTPException(
        status_code=403,
        detail="You must complete the test before viewing solutions"
    )
```

### Checkpoint 3: Download PDF (`/tests/{test_id}/download-solutions`)
**Requirements:**
- ✅ Valid JWT token
- ✅ Purchase status = "completed" ← **NEWLY ADDED**
- ✅ Test must be completed

**Code:**
```python
# CRITICAL: Check payment status
purchase = await db.purchases.find_one({
    "student_id": current_user.id,
    "test_id": test_id,
    "status": "completed"  # MUST be completed payment
})
if not purchase:
    raise HTTPException(
        status_code=403,
        detail="You must complete the payment before downloading solutions"
    )
```

### Checkpoint 4: My Tests List (`/my-tests`)
**Only shows completed purchases:**
```python
purchases = await db.purchases.find({
    "student_id": current_user.id,
    "status": "completed"  # Only verified payments
}).to_list(1000)
```

---

## 🔒 Database Schema

### Purchase Model:
```python
{
    "id": "uuid",
    "student_id": "user-uuid",
    "test_id": "test-uuid",
    "amount": 49.00,
    "status": "pending" | "completed" | "failed",
    "razorpay_order_id": "order_xxx",
    "razorpay_payment_id": "pay_xxx",  # Set after payment
    "created_at": "timestamp",
    "completed_at": "timestamp"  # Set after verification
}
```

**Status Values:**
- `pending`: Order created, payment not completed
- `completed`: Payment verified via Razorpay signature ✅
- `failed`: Payment failed or cancelled

---

## 🎯 Attack Scenarios Prevented

### Scenario 1: Payment Window Closed
**Attack:** Student clicks "Purchase", payment window opens, student closes it
**Prevention:** Purchase remains "pending", student CANNOT access test/solutions

### Scenario 2: Fake Payment Data
**Attack:** Student tries to call verify-payment with fake data
**Prevention:** Razorpay signature verification fails, status stays "pending"

### Scenario 3: Direct API Access
**Attack:** Student tries to call `/test-solutions/{test_id}` directly
**Prevention:** Backend checks purchase status = "completed", blocks access

### Scenario 4: Manipulated Purchase Record
**Attack:** Student tries to modify database directly
**Prevention:** 
- MongoDB access only from backend
- JWT authentication required
- Role-based access control

### Scenario 5: Replay Attack
**Attack:** Student tries to reuse old payment verification
**Prevention:** Razorpay order IDs are unique, already-verified orders won't create duplicate purchases

---

## 🚀 Payment Verification Process

### Razorpay Signature Verification:

```python
# What Razorpay sends after payment:
{
    "razorpay_order_id": "order_xxx",
    "razorpay_payment_id": "pay_xxx",
    "razorpay_signature": "cryptographic_signature"
}

# Backend verification:
params_dict = {
    'razorpay_order_id': verification.razorpay_order_id,
    'razorpay_payment_id': verification.razorpay_payment_id,
    'razorpay_signature': verification.razorpay_signature
}

# This will throw SignatureVerificationError if tampered
razorpay_client.utility.verify_payment_signature(params_dict)

# Only if verification succeeds:
await db.purchases.update_one(
    {"razorpay_order_id": order_id, "status": "pending"},
    {"$set": {"status": "completed", "completed_at": datetime.now()}}
)
```

**How Signature Works:**
- Razorpay creates HMAC-SHA256 signature using secret key
- Signature includes order_id + payment_id
- Backend verifies signature using same secret key
- If signature doesn't match = payment was tampered = REJECTED

---

## 📊 Access Control Matrix

| Action | JWT Token | Purchase Exists | Purchase Status | Test Completed |
|--------|-----------|----------------|-----------------|----------------|
| View Public Tests | ❌ | ❌ | ❌ | ❌ |
| Purchase Test | ✅ | ❌ | ❌ | ❌ |
| View My Tests | ✅ | ✅ | "completed" | ❌ |
| Take Test | ✅ | ✅ | "completed" | ❌ |
| View Solutions | ✅ | ✅ | "completed" | ✅ |
| Download PDF | ✅ | ✅ | "completed" | ✅ |

---

## 🔍 Testing the Security

### Test Case 1: Incomplete Payment
```
1. Login as student
2. Add test to cart
3. Click checkout
4. Close Razorpay payment window
5. Try to access /my-tests
   ✅ EXPECTED: Test NOT listed
6. Try to access /tests/{test_id}/take
   ✅ EXPECTED: 403 Forbidden "Test not purchased"
```

### Test Case 2: Completed Payment
```
1. Login as student
2. Add test to cart
3. Click checkout
4. Complete Razorpay payment
5. Frontend calls /cart/verify-payment
6. Backend verifies signature
7. Purchase status updated to "completed"
8. Try to access /my-tests
   ✅ EXPECTED: Test IS listed
9. Try to access /tests/{test_id}/take
   ✅ EXPECTED: Test page loads successfully
```

### Test Case 3: Solution Access Without Payment
```
1. Somehow obtain test_id
2. Try to access /test-solutions/{test_id}
   ✅ EXPECTED: 403 Forbidden "You must complete the payment"
```

### Test Case 4: PDF Download Without Payment
```
1. Somehow obtain test_id
2. Try to access /tests/{test_id}/download-solutions
   ✅ EXPECTED: 403 Forbidden "You must complete the payment"
```

---

## 🎯 Frontend Integration

### Payment Flow in Frontend:

```javascript
// 1. Checkout creates Razorpay order
const checkoutResponse = await axios.post('/api/cart/checkout');
const { order_id, amount } = checkoutResponse.data;

// 2. Open Razorpay payment window
const options = {
  key: RAZORPAY_KEY_ID,
  amount: amount * 100,
  order_id: order_id,
  handler: async function (response) {
    // 3. Payment successful - verify it
    await axios.post('/api/cart/verify-payment', {
      razorpay_order_id: response.razorpay_order_id,
      razorpay_payment_id: response.razorpay_payment_id,
      razorpay_signature: response.razorpay_signature
    });
    
    // 4. Only now can student access tests
    toast.success('Payment successful!');
    navigate('/dashboard');
  }
};

const rzp = new Razorpay(options);
rzp.open();
```

---

## 📝 Audit Log (What Was Fixed)

### Files Modified:
1. `/app/backend/server.py`

### Changes Made:

**1. `/test-solutions/{test_id}` endpoint (Line 1286-1337):**
- **BEFORE:** Only checked test completion
- **AFTER:** Checks payment status = "completed" FIRST, then test completion
- **Impact:** Prevents unpaid students from viewing solutions

**2. `/tests/{test_id}/download-solutions` endpoint (Line 1339-1520):**
- **BEFORE:** Only checked purchase existence (not status)
- **AFTER:** Checks payment status = "completed" before allowing download
- **Impact:** Prevents unpaid students from downloading PDFs

---

## ✅ Security Checklist

- [x] Purchase records created with status="pending"
- [x] Razorpay signature verification implemented
- [x] Purchase status updated to "completed" only after verification
- [x] Test access requires status="completed"
- [x] Solution access requires status="completed"
- [x] PDF download requires status="completed"
- [x] My Tests list filters by status="completed"
- [x] No hardcoded bypasses or test modes
- [x] All endpoints use JWT authentication
- [x] Role-based access control (students only)
- [x] Database queries properly filtered
- [x] Error messages don't leak sensitive info

---

## 🚨 Important Notes

### DO NOT:
- ❌ Remove status checks from any endpoint
- ❌ Allow status="pending" purchases to access tests
- ❌ Skip Razorpay signature verification
- ❌ Create purchases with status="completed" without payment
- ❌ Bypass payment checks in "test mode"

### DO:
- ✅ Always verify Razorpay signatures
- ✅ Always check purchase status = "completed"
- ✅ Log all payment attempts for audit
- ✅ Monitor failed payment verifications
- ✅ Keep Razorpay secret key secure

---

## 📊 Monitoring & Alerts

### What to Monitor:
1. **Failed Payment Verifications:** 
   - Multiple failures from same user = potential attack
2. **Pending Purchases:**
   - Too many pending = payment flow issues
3. **403 Errors on Test Access:**
   - Normal for unpaid students
   - Spike = potential attack attempt

---

## 🔐 Production Checklist

Before going live:
- [ ] Razorpay keys properly configured in .env
- [ ] Test complete payment flow end-to-end
- [ ] Test cancelled payment flow
- [ ] Test failed payment flow
- [ ] Verify all endpoints check payment status
- [ ] Test PDF download with/without payment
- [ ] Test solution access with/without payment
- [ ] Review error messages (no sensitive info leak)
- [ ] Set up payment monitoring/alerts
- [ ] Document payment refund process

---

**Last Updated:** January 2025
**Security Level:** HIGH
**Status:** ✅ SECURED

---

## 📞 Quick Reference

**Payment Status Values:**
- `pending` = Payment initiated but not completed
- `completed` = Payment verified and confirmed ✅
- `failed` = Payment failed

**Access Rule:**
- No access to test content unless purchase status = `completed`

**Verification:**
- All payments verified via Razorpay cryptographic signature
- No manual status updates without verification

---

End of Security Documentation
