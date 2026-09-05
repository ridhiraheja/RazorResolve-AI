"""
RazorResolve AI  Synthetic Seed Data Generator
Generates realistic demo data using Indian names, INR currency, and plausible
e-commerce scenarios covering all 6 demo scenarios from the spec.
"""
import asyncio
import uuid
import random
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.database import init_db, AsyncSessionLocal, engine, Base
from app.models import (
    Customer, CustomerTier, Order, OrderStatus,
    Product, ProductCategory,
    Payment, PaymentEvent, WebhookEvent, PaymentStatus, PaymentMethod, FailureReason,
    Incident, IncidentType, IncidentSeverity, IncidentStatus,
    AIDecision, AuditLog, DecisionType,
    Cart, CartStatus,
)

#  helpers 
def uid(): return str(uuid.uuid4())
def now(): return datetime.utcnow()
def ago(minutes=0, hours=0, days=0):
    return now() - timedelta(minutes=minutes, hours=hours, days=days)

random.seed(42)

#  Indian first/last names 
FIRST_NAMES = [
    "Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Ayaan","Krishna","Ishaan",
    "Priya","Ananya","Diya","Isha","Meera","Kavya","Avni","Riya","Pooja","Shreya",
    "Rahul","Rohit","Amit","Suresh","Vikram","Deepak","Nikhil","Rajesh","Sanjay","Manish",
    "Anjali","Sunita","Rekha","Geeta","Lakshmi","Nisha","Usha","Radha","Sita","Kamla",
    "Akash","Gaurav","Harish","Naveen","Pankaj","Rajiv","Sandeep","Tarun","Umesh","Varun",
    "Divya","Kavita","Madhuri","Nidhi","Pallavi","Richa","Smita","Tanvi","Vandana","Yashoda",
    "Abhinav","Chirag","Dhruv","Ekta","Farida","Gaurav","Hemant","Indira","Jatin","Kirti",
    "Lavanya","Mohit","Neha","Omkar","Pratik","Qasim","Ritesh","Sahil","Tejas","Urvashi",
    "Vidya","Wasim","Xavier","Yash","Zara","Aisha","Bhavna","Chetan","Deepika","Esha",
    "Faraz","Girish","Harsha","Ishan","Juhi","Karan","Lata","Milan","Natasha","Ojas",
]
LAST_NAMES = [
    "Sharma","Verma","Patel","Singh","Kumar","Gupta","Joshi","Mehta","Nair","Iyer",
    "Reddy","Rao","Pillai","Menon","Chaudhary","Mishra","Tiwari","Yadav","Saxena","Malhotra",
    "Agarwal","Bansal","Chopra","Dubey","Ghosh","Hussain","Jain","Kapoor","Lal","Mukherjee",
    "Naidu","Oberoi","Pandey","Qureshi","Rastogi","Sethi","Thakur","Upadhyay","Walia","Zaffar",
    "Anand","Batra","Chauhan","Desai","Fernandes","Garg","Hegde","Iyengar","Jaiswal","Khanna",
]
CITIES = ["Mumbai","Delhi","Bangalore","Hyderabad","Chennai","Pune","Kolkata","Ahmedabad","Jaipur","Lucknow"]
STATES = ["Maharashtra","Delhi","Karnataka","Telangana","Tamil Nadu","Maharashtra","West Bengal","Gujarat","Rajasthan","Uttar Pradesh"]

def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def random_email(name, idx=0):
    parts = name.lower().split()
    return f"{parts[0]}.{parts[1]}.{idx}@{'gmail.com' if random.random()>0.3 else 'yahoo.in'}"

def random_phone():
    return f"+91{random.randint(7000000000,9999999999)}"

def random_city():
    i = random.randint(0, len(CITIES)-1)
    return CITIES[i], STATES[i]

#  Products catalog 
PRODUCTS_DATA = [
    # Electronics
    {"name":"Samsung Galaxy S23 Ultra","cat":ProductCategory.ELECTRONICS,"price":124999,"brand":"Samsung","tags":["smartphone","android","camera"],"rating":4.6,"review_count":2847},
    {"name":"Apple iPhone 15 Pro","cat":ProductCategory.ELECTRONICS,"price":134900,"brand":"Apple","tags":["smartphone","ios","premium"],"rating":4.8,"review_count":4123},
    {"name":"OnePlus 12R","cat":ProductCategory.ELECTRONICS,"price":39999,"brand":"OnePlus","tags":["smartphone","android","fast-charging"],"rating":4.4,"review_count":1923},
    {"name":"Redmi Note 13 Pro+","cat":ProductCategory.ELECTRONICS,"price":29999,"brand":"Redmi","tags":["smartphone","android","budget"],"rating":4.3,"review_count":3241},
    {"name":"Apple MacBook Air M2","cat":ProductCategory.ELECTRONICS,"price":114900,"brand":"Apple","tags":["laptop","macos","productivity"],"rating":4.9,"review_count":1876},
    {"name":"Dell XPS 15","cat":ProductCategory.ELECTRONICS,"price":149990,"brand":"Dell","tags":["laptop","windows","coding"],"rating":4.5,"review_count":987},
    {"name":"ASUS VivoBook 15","cat":ProductCategory.ELECTRONICS,"price":54990,"brand":"ASUS","tags":["laptop","windows","student"],"rating":4.2,"review_count":2134},
    {"name":"HP Pavilion x360","cat":ProductCategory.ELECTRONICS,"price":64990,"brand":"HP","tags":["laptop","2-in-1","touch"],"rating":4.1,"review_count":1567},
    {"name":"Sony WH-1000XM5 Noise Cancelling Headphones","cat":ProductCategory.ELECTRONICS,"price":29990,"brand":"Sony","tags":["headphones","earphones","noise-cancelling","wireless","bluetooth","audio"],"rating":4.7,"review_count":3421},
    {"name":"boAt Rockerz 450 Wireless Headphones","cat":ProductCategory.ELECTRONICS,"price":1499,"brand":"boAt","tags":["headphones","earphones","wireless","budget","bluetooth","audio"],"rating":4.0,"review_count":8921},
    {"name":"boAt Airdopes 141 Wireless Earbuds","cat":ProductCategory.ELECTRONICS,"price":1299,"brand":"boAt","tags":["earphones","earbuds","wireless-earbuds","bluetooth","budget","in-ear"],"rating":4.3,"review_count":9420},
    {"name":"Apple AirPods Pro (2nd Gen)","cat":ProductCategory.ELECTRONICS,"price":24900,"brand":"Apple","tags":["earphones","earbuds","wireless-earbuds","bluetooth","anc","apple","airpods"],"rating":4.8,"review_count":5120},
    {"name":"Sony WF-1000XM5 Wireless Earbuds","cat":ProductCategory.ELECTRONICS,"price":24990,"brand":"Sony","tags":["earphones","earbuds","wireless-earbuds","bluetooth","anc","audio"],"rating":4.7,"review_count":1840},
    {"name":"OnePlus Buds Pro 2 TWS","cat":ProductCategory.ELECTRONICS,"price":9999,"brand":"OnePlus","tags":["earphones","earbuds","wireless-earbuds","bluetooth","anc"],"rating":4.5,"review_count":2310},
    {"name":"Realme Buds T300 Earbuds","cat":ProductCategory.ELECTRONICS,"price":2299,"brand":"Realme","tags":["earphones","earbuds","wireless-earbuds","bluetooth","budget"],"rating":4.2,"review_count":3120},
    {"name":"Samsung 55\" 4K QLED TV","cat":ProductCategory.ELECTRONICS,"price":79990,"brand":"Samsung","tags":["tv","4k","smart","television"],"rating":4.5,"review_count":1234},
    {"name":"Mi Smart TV 5X 50\"","cat":ProductCategory.ELECTRONICS,"price":34999,"brand":"Xiaomi","tags":["tv","smart","budget","television"],"rating":4.2,"review_count":2341},
    {"name":"Apple iPad Air M1","cat":ProductCategory.ELECTRONICS,"price":59900,"brand":"Apple","tags":["tablet","ios","productivity"],"rating":4.7,"review_count":1456},
    {"name":"Samsung Galaxy Tab S9","cat":ProductCategory.ELECTRONICS,"price":72999,"brand":"Samsung","tags":["tablet","android","amoled"],"rating":4.4,"review_count":876},
    {"name":"Canon EOS R50","cat":ProductCategory.ELECTRONICS,"price":74990,"brand":"Canon","tags":["camera","mirrorless","photography"],"rating":4.6,"review_count":543},
    {"name":"GoPro Hero 12","cat":ProductCategory.ELECTRONICS,"price":44990,"brand":"GoPro","tags":["camera","action","waterproof"],"rating":4.5,"review_count":765},
    {"name":"Logitech MX Master 3","cat":ProductCategory.ELECTRONICS,"price":8495,"brand":"Logitech","tags":["mouse","wireless","productivity"],"rating":4.8,"review_count":4321},
    {"name":"Keychron K2 Keyboard","cat":ProductCategory.ELECTRONICS,"price":6500,"brand":"Keychron","tags":["keyboard","mechanical","bluetooth"],"rating":4.6,"review_count":2198},
    {"name":"Acer Nitro 5 Gaming Laptop","cat":ProductCategory.ELECTRONICS,"price":69990,"brand":"Acer","tags":["laptop","gaming","rtx","coding","gpu"],"rating":4.3,"review_count":3421},
    {"name":"ASUS ROG Phone 8","cat":ProductCategory.ELECTRONICS,"price":89999,"brand":"ASUS","tags":["smartphone","gaming","performance","mobile"],"rating":4.5,"review_count":987},
    # Fashion
    {"name":"Levi's 512 Slim Tapered Jeans","cat":ProductCategory.FASHION,"price":3499,"brand":"Levi's","tags":["jeans","men","casual"],"rating":4.3,"review_count":5432},
    {"name":"Nike Air Max 270","cat":ProductCategory.FASHION,"price":10995,"brand":"Nike","tags":["shoes","running","sports"],"rating":4.5,"review_count":3241},
    {"name":"Adidas Ultraboost 22","cat":ProductCategory.FASHION,"price":17999,"brand":"Adidas","tags":["shoes","running","comfort"],"rating":4.6,"review_count":2134},
    {"name":"Zara Floral Midi Dress","cat":ProductCategory.FASHION,"price":3990,"brand":"Zara","tags":["dress","women","floral"],"rating":4.1,"review_count":1876},
    {"name":"H&M Oversized Hoodie","cat":ProductCategory.FASHION,"price":1999,"brand":"H&M","tags":["hoodie","unisex","casual"],"rating":4.2,"review_count":4321},
    {"name":"Raymond Formal Shirt","cat":ProductCategory.FASHION,"price":1899,"brand":"Raymond","tags":["shirt","men","formal"],"rating":4.0,"review_count":2876},
    {"name":"Puma Sports T-Shirt","cat":ProductCategory.FASHION,"price":999,"brand":"Puma","tags":["tshirt","sports","dryfit"],"rating":4.1,"review_count":6543},
    {"name":"Fabindia Ethnic Kurta","cat":ProductCategory.FASHION,"price":1499,"brand":"Fabindia","tags":["kurta","ethnic","cotton"],"rating":4.4,"review_count":3219},
    # Home
    {"name":"Dyson V12 Detect Slim","cat":ProductCategory.HOME,"price":56900,"brand":"Dyson","tags":["vacuum","cordless","home"],"rating":4.7,"review_count":876},
    {"name":"Philips Air Fryer HD9270","cat":ProductCategory.HOME,"price":8995,"brand":"Philips","tags":["airfryer","kitchen","healthy"],"rating":4.5,"review_count":4567},
    {"name":"Instant Pot Duo 7-in-1","cat":ProductCategory.HOME,"price":7999,"brand":"Instant Pot","tags":["pressure-cooker","kitchen","multipurpose"],"rating":4.6,"review_count":3421},
    {"name":"IKEA KALLAX Shelf Unit","cat":ProductCategory.HOME,"price":5990,"brand":"IKEA","tags":["furniture","storage","shelf"],"rating":4.3,"review_count":2134},
    {"name":"Havells Ceiling Fan 1200mm","cat":ProductCategory.HOME,"price":2999,"brand":"Havells","tags":["fan","ceiling","energy-saving"],"rating":4.2,"review_count":5432},
    {"name":"Prestige Gas Stove 4 Burner","cat":ProductCategory.HOME,"price":4499,"brand":"Prestige","tags":["gas-stove","kitchen","cooking"],"rating":4.4,"review_count":3876},
    # Sports
    {"name":"Cosco Football Size 5","cat":ProductCategory.SPORTS,"price":799,"brand":"Cosco","tags":["football","outdoor","sports"],"rating":4.1,"review_count":2341},
    {"name":"Decathlon Yoga Mat 8mm","cat":ProductCategory.SPORTS,"price":1299,"brand":"Decathlon","tags":["yoga","mat","fitness"],"rating":4.5,"review_count":5678},
    {"name":"Yonex Arcsaber 11 Racket","cat":ProductCategory.SPORTS,"price":8999,"brand":"Yonex","tags":["badminton","racket","professional"],"rating":4.7,"review_count":1234},
    # Books
    {"name":"Atomic Habits by James Clear","cat":ProductCategory.BOOKS,"price":399,"brand":"Penguin","tags":["self-help","productivity","habits"],"rating":4.8,"review_count":12453},
    {"name":"Zero to One by Peter Thiel","cat":ProductCategory.BOOKS,"price":349,"brand":"Crown Business","tags":["startup","business","innovation"],"rating":4.6,"review_count":8765},
    {"name":"The Psychology of Money","cat":ProductCategory.BOOKS,"price":399,"brand":"Jaico","tags":["finance","money","psychology"],"rating":4.7,"review_count":9876},
]

#  Payment failure scenarios 
FAILURE_SCENARIOS = [
    (FailureReason.TECHNICAL_ERROR, "Payment processing failed due to a temporary gateway issue"),
    (FailureReason.TIMEOUT, "Payment request timed out after 5 minutes"),
    (FailureReason.BANK_DECLINE, "Transaction declined by issuing bank"),
    (FailureReason.INSUFFICIENT_FUNDS, "Insufficient balance in account"),
    (FailureReason.NETWORK_ERROR, "Network error during payment authorization"),
    (FailureReason.UPI_FAILURE, "UPI transaction failed  VPA not responding"),
    (FailureReason.INVALID_CARD, "Card validation failed  incorrect details"),
    (FailureReason.FRAUD_SUSPECTED, "Transaction flagged by fraud detection system"),
]

RECOVERY_ACTIONS = {
    FailureReason.TECHNICAL_ERROR: "Retry payment via alternate method (UPI/Card)",
    FailureReason.TIMEOUT: "Re-initiate payment session with extended timeout",
    FailureReason.BANK_DECLINE: "Suggest alternate bank/payment method",
    FailureReason.INSUFFICIENT_FUNDS: "Offer EMI or part-payment options",
    FailureReason.NETWORK_ERROR: "Auto-retry with exponential backoff",
    FailureReason.UPI_FAILURE: "Switch to card or netbanking payment",
    FailureReason.INVALID_CARD: "Request card details re-entry",
    FailureReason.FRAUD_SUSPECTED: "Route for manual review  escalate to compliance",
}

CONFIDENCE_BY_FAILURE = {
    FailureReason.TECHNICAL_ERROR: 0.94,
    FailureReason.TIMEOUT: 0.91,
    FailureReason.BANK_DECLINE: 0.87,
    FailureReason.INSUFFICIENT_FUNDS: 0.89,
    FailureReason.NETWORK_ERROR: 0.92,
    FailureReason.UPI_FAILURE: 0.88,
    FailureReason.INVALID_CARD: 0.85,
    FailureReason.FRAUD_SUSPECTED: 0.78,
}

INTERVENTIONS = [
    "Send personalized discount code (10% off)",
    "Trigger urgency notification  only 3 items left in stock",
    "Offer free express shipping for 2 hours",
    "Show social proof  847 others viewing this product",
    "Recommend complementary product bundle",
    "Send cart abandonment email with product images",
    "Offer buy-now-pay-later option",
]


#  Main seeder 
async def seed():
    print(" Initialising database schema ")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await init_db()
    print(" Schema created")

    async with AsyncSessionLocal() as db:
        #  1. Products 
        print(" Seeding products ")
        product_ids = []
        products_map = {}
        for i, p in enumerate(PRODUCTS_DATA):
            pid = uid()
            product_ids.append(pid)
            prod = Product(
                id=pid,
                name=p["name"],
                category=p["cat"],
                price=p["price"],
                original_price=round(p["price"] * random.uniform(1.1, 1.3)),
                brand=p["brand"],
                tags=p["tags"],
                rating=p["rating"],
                review_count=p["review_count"],
                stock=random.randint(5, 200),
                popularity_score=round(random.uniform(0.4, 0.98), 2),
                conversion_rate=round(random.uniform(0.08, 0.28), 2),
            )
            products_map[pid] = prod
            db.add(prod)

        # Set upsell / crosssell links
        for pid in product_ids:
            prod = products_map[pid]
            others = [x for x in product_ids if x != pid]
            prod.upsell_ids = random.sample(others, min(3, len(others)))
            prod.crosssell_ids = random.sample(others, min(4, len(others)))

        await db.commit()
        print(f"   {len(product_ids)} products")

        #  2. Customers 
        print(" Seeding customers ")
        customer_ids = []
        for c_idx in range(100):
            name = random_name()
            city, state = random_city()
            cid = uid()
            customer_ids.append(cid)
            tier_weights = [0.4, 0.3, 0.2, 0.1]
            tier = random.choices(list(CustomerTier), weights=tier_weights)[0]
            total_orders = random.randint(1, 40)
            avg_val = random.uniform(800, 25000)
            db.add(Customer(
                id=cid,
                name=name,
                email=random_email(name, c_idx),
                phone=random_phone(),
                city=city,
                state=state,
                tier=tier,
                total_orders=total_orders,
                total_spent=round(total_orders * avg_val, 2),
                avg_order_value=round(avg_val, 2),
                created_at=ago(days=random.randint(30, 730)),
                last_active=ago(hours=random.randint(0, 72)),
            ))
        await db.commit()
        print(f"   {len(customer_ids)} customers")

        #  3. Orders + Payments 
        print(" Seeding orders and payments ")
        order_ids = []
        payment_ids = []

        def make_items():
            n = random.randint(1, 4)
            items = []
            for _ in range(n):
                pid = random.choice(product_ids)
                p = products_map[pid]
                qty = random.randint(1, 3)
                items.append({"product_id": pid, "name": p.name, "qty": qty, "price": p.price})
            return items

        def items_total(items):
            return round(sum(i["price"] * i["qty"] for i in items), 2)

        # 120 normal/mixed orders
        for idx in range(120):
            cid = random.choice(customer_ids)
            items = make_items()
            total = items_total(items)
            oid = uid()
            order_ids.append(oid)

            # Mostly completed, some failed
            if idx < 80:
                ostatus = OrderStatus.COMPLETED
                pstatus = PaymentStatus.CAPTURED
                freason = FailureReason.NONE
                fmsg = None
                captured_at = ago(days=random.randint(1, 60))
                webhook_ok = True
            elif idx < 100:
                ostatus = OrderStatus.FAILED
                freason, fmsg = random.choice(FAILURE_SCENARIOS)
                pstatus = PaymentStatus.FAILED
                captured_at = None
                webhook_ok = False
            else:
                ostatus = OrderStatus.PROCESSING
                pstatus = PaymentStatus.AUTHORIZED
                freason = FailureReason.NONE
                fmsg = None
                captured_at = None
                webhook_ok = True

            db.add(Order(
                id=oid,
                customer_id=cid,
                status=ostatus,
                total_amount=total,
                items=items,
                shipping_address={"city": "Mumbai", "state": "Maharashtra", "pincode": "400001"},
                created_at=ago(days=random.randint(1, 90)),
            ))

            pid = uid()
            payment_ids.append(pid)
            method = random.choice(list(PaymentMethod))
            db.add(Payment(
                id=pid,
                order_id=oid,
                customer_id=cid,
                amount=total,
                method=method,
                status=pstatus,
                failure_reason=freason,
                failure_message=fmsg,
                gateway_payment_id=f"rzp_sim_{pid[:8]}",
                attempt_count=1,
                is_webhook_delivered=webhook_ok,
                webhook_attempts=1 if webhook_ok else random.randint(1, 5),
                created_at=ago(days=random.randint(1, 90)),
                captured_at=captured_at,
                failed_at=None if pstatus != PaymentStatus.FAILED else ago(days=random.randint(1, 30)),
            ))

        await db.commit()
        print(f"   {len(order_ids)} orders, {len(payment_ids)} payments")

        #  DEMO SCENARIO 2: payment failed  AI recovery 
        print(" Seeding demo scenarios ")

        # SCENARIO 2  Technical failure with recovery opportunity
        s2_cid = customer_ids[0]
        s2_items = [{"product_id": product_ids[4], "name": PRODUCTS_DATA[4]["name"], "qty": 1, "price": PRODUCTS_DATA[4]["price"]}]
        s2_total = PRODUCTS_DATA[4]["price"]  # 1,14,900 MacBook
        s2_oid = uid()
        s2_pid = uid()
        db.add(Order(id=s2_oid, customer_id=s2_cid, status=OrderStatus.FAILED,
                     total_amount=s2_total, items=s2_items,
                     created_at=ago(minutes=25)))
        db.add(Payment(id=s2_pid, order_id=s2_oid, customer_id=s2_cid,
                       amount=s2_total, method=PaymentMethod.UPI,
                       status=PaymentStatus.FAILED,
                       failure_reason=FailureReason.TECHNICAL_ERROR,
                       failure_message="Payment gateway returned error code TECH_FAILURE_503",
                       gateway_payment_id=f"rzp_sim_{s2_pid[:8]}",
                       attempt_count=3,
                       created_at=ago(minutes=25),
                       failed_at=ago(minutes=22)))
        for evt_name in ["payment.created", "payment.attempted", "payment.failed"]:
            db.add(PaymentEvent(id=uid(), payment_id=s2_pid, event_type=evt_name,
                                payload={"amount": s2_total, "method": "upi"},
                                created_at=ago(minutes=random.randint(20, 25))))

        s2_incident_id = uid()
        s2_decision_id = uid()
        db.add(Incident(
            id=s2_incident_id, type=IncidentType.PAYMENT_FAILED,
            severity=IncidentSeverity.HIGH, status=IncidentStatus.ACTION_REQUIRED,
            customer_id=s2_cid, order_id=s2_oid, payment_id=s2_pid,
            amount_at_risk=s2_total,
            root_cause="Temporary payment gateway failure (503 error). No successful capture recorded.",
            confidence_score=0.94,
            evidence=["3 payment attempts in 25 minutes", "All failed with TECH_FAILURE_503",
                      "No successful capture event found", "Gateway status page shows partial outage"],
            recommended_action="Retry payment via alternate method (Card/NetBanking)",
            expected_recovery=s2_total,
            risk_level="low",
            auto_executable=True,
            requires_approval=False,
            policy_result="ALLOW",
            ai_explanation="Payment failed due to temporary processing issue. No successful transaction exists for this order so retrying via alternate method is safe and low risk.",
            created_at=ago(minutes=22),
        ))
        db.add(AIDecision(
            id=s2_decision_id, incident_id=s2_incident_id,
            agent_name="PaymentInvestigationAgent",
            decision_type=DecisionType.PAYMENT_DIAGNOSIS,
            observation="3 UPI payment attempts failed within 25 minutes. Gateway returned 503 on all attempts.",
            reasoning="Pattern of 503 errors strongly correlates with temporary gateway outage rather than customer-side issue. Alternate payment method retry is appropriate.",
            decision="Recommend alternate payment method retry",
            action_taken="Notification sent to customer with Card/NetBanking retry link",
            policy_result="ALLOW",
            confidence_score=0.94,
            expected_impact=s2_total,
            evidence={"failure_pattern": "TECH_FAILURE_503", "attempts": 3, "time_window_minutes": 25},
            created_at=ago(minutes=20),
        ))

        # SCENARIO 3  Abandoned checkout
        s3_cid = customer_ids[1]
        s3_items = [
            {"product_id": product_ids[1], "name": PRODUCTS_DATA[1]["name"], "qty": 1, "price": PRODUCTS_DATA[1]["price"]},
            {"product_id": product_ids[9], "name": PRODUCTS_DATA[9]["name"], "qty": 1, "price": PRODUCTS_DATA[9]["price"]},
        ]
        s3_total = PRODUCTS_DATA[1]["price"] + PRODUCTS_DATA[9]["price"]
        s3_cart_id = uid()
        s3_incident_id = uid()
        db.add(Cart(
            id=s3_cart_id, customer_id=s3_cid, status=CartStatus.ABANDONED,
            items=s3_items, total_value=s3_total, item_count=2,
            intent_score=0.82, conversion_probability=0.74,
            recommended_intervention="Send personalized discount (8% off) with urgency trigger",
            expected_recovery=round(s3_total * 0.74),
            abandoned_at=ago(hours=2),
            created_at=ago(hours=3),
        ))
        db.add(Incident(
            id=s3_incident_id, type=IncidentType.CHECKOUT_ABANDONED,
            severity=IncidentSeverity.MEDIUM, status=IncidentStatus.INVESTIGATING,
            customer_id=s3_cid, amount_at_risk=s3_total,
            root_cause="Customer added high-value items (iPhone 15 Pro + boAt headphones) and reached checkout but left 2 hours ago.",
            confidence_score=0.82,
            evidence=["Cart value 1,36,399", "Customer is Gold tier with 12 previous purchases",
                      "Abandoned at payment method selection step", "Previously purchased similar products"],
            recommended_action="Send 8% discount code with 6-hour expiry + free express shipping",
            expected_recovery=round(s3_total * 0.74),
            risk_level="low",
            auto_executable=True,
            requires_approval=False,
            policy_result="ALLOW",
            ai_explanation="High-intent customer (Gold tier, 12 orders) abandoned at payment step with 1,36,399 cart. High conversion probability (74%) justifies immediate personalized outreach.",
            created_at=ago(hours=2),
        ))

        # SCENARIO 4  Webhook failure
        s4_cid = customer_ids[2]
        s4_items = [{"product_id": product_ids[10], "name": PRODUCTS_DATA[10]["name"], "qty": 1, "price": PRODUCTS_DATA[10]["price"]}]
        s4_total = PRODUCTS_DATA[10]["price"]  # 79,990 Samsung TV
        s4_oid = uid()
        s4_pid = uid()
        s4_webhook_id = uid()
        s4_incident_id = uid()
        db.add(Order(id=s4_oid, customer_id=s4_cid, status=OrderStatus.PROCESSING,
                     total_amount=s4_total, items=s4_items, created_at=ago(hours=6)))
        db.add(Payment(id=s4_pid, order_id=s4_oid, customer_id=s4_cid,
                       amount=s4_total, method=PaymentMethod.CARD,
                       status=PaymentStatus.CAPTURED,
                       failure_reason=FailureReason.NONE,
                       gateway_payment_id=f"rzp_sim_{s4_pid[:8]}",
                       is_webhook_delivered=False,
                       webhook_attempts=5,
                       created_at=ago(hours=6),
                       captured_at=ago(hours=6)))
        db.add(WebhookEvent(
            id=s4_webhook_id, payment_id=s4_pid,
            event_type="payment.captured",
            status="failed",
            payload={"payment_id": s4_pid, "amount": s4_total, "event": "payment.captured"},
            delivery_attempts=5,
            last_attempt_at=ago(minutes=30),
            created_at=ago(hours=6),
        ))
        db.add(Incident(
            id=s4_incident_id, type=IncidentType.WEBHOOK_FAILURE,
            severity=IncidentSeverity.HIGH, status=IncidentStatus.ACTION_REQUIRED,
            customer_id=s4_cid, order_id=s4_oid, payment_id=s4_pid,
            amount_at_risk=s4_total,
            root_cause="Payment successfully captured (79,990) but webhook delivery failed after 5 attempts. Order remains in PROCESSING state.",
            confidence_score=0.97,
            evidence=["Payment status: CAPTURED in gateway", "Order status: PROCESSING (not updated)",
                      "5 webhook delivery failures in 6 hours", "Customer has not received confirmation"],
            recommended_action="Replay webhook event  safe since payment is confirmed captured",
            expected_recovery=s4_total,
            risk_level="low",
            auto_executable=True,
            requires_approval=False,
            policy_result="ALLOW",
            ai_explanation="Payment captured confirmed via gateway. Order stuck due to webhook delivery failure. Replaying the webhook event will update order state and trigger confirmation  no financial risk.",
            created_at=ago(hours=5, minutes=50),
        ))

        # SCENARIO 5  Duplicate payment
        s5_cid = customer_ids[3]
        s5_items = [{"product_id": product_ids[2], "name": PRODUCTS_DATA[2]["name"], "qty": 1, "price": PRODUCTS_DATA[2]["price"]}]
        s5_total = PRODUCTS_DATA[2]["price"]  # 39,999 OnePlus
        s5_oid = uid()
        s5_pid_1 = uid()
        s5_pid_2 = uid()
        s5_incident_id = uid()
        db.add(Order(id=s5_oid, customer_id=s5_cid, status=OrderStatus.COMPLETED,
                     total_amount=s5_total, items=s5_items, created_at=ago(hours=3)))
        db.add(Payment(id=s5_pid_1, order_id=s5_oid, customer_id=s5_cid,
                       amount=s5_total, method=PaymentMethod.CARD,
                       status=PaymentStatus.CAPTURED,
                       failure_reason=FailureReason.NONE,
                       gateway_payment_id=f"rzp_sim_{s5_pid_1[:8]}",
                       is_webhook_delivered=True,
                       created_at=ago(hours=3),
                       captured_at=ago(hours=3)))
        db.add(Payment(id=s5_pid_2, order_id=s5_oid, customer_id=s5_cid,
                       amount=s5_total, method=PaymentMethod.CARD,
                       status=PaymentStatus.CAPTURED,
                       failure_reason=FailureReason.NONE,
                       gateway_payment_id=f"rzp_sim_{s5_pid_2[:8]}",
                       is_webhook_delivered=True,
                       created_at=ago(hours=2, minutes=58),
                       captured_at=ago(hours=2, minutes=57)))
        db.add(Incident(
            id=s5_incident_id, type=IncidentType.DUPLICATE_PAYMENT,
            severity=IncidentSeverity.CRITICAL, status=IncidentStatus.ESCALATED,
            customer_id=s5_cid, order_id=s5_oid,
            amount_at_risk=s5_total,
            root_cause="Two successful payment captures detected for same order within a 3-minute window. Possible double-charge.",
            confidence_score=0.89,
            evidence=[f"Payment {s5_pid_1[:8]}: CAPTURED {s5_total} at T+0", 
                      f"Payment {s5_pid_2[:8]}: CAPTURED {s5_total} at T+3min",
                      "Same order_id, same amount, same card type",
                      "Customer may have clicked Pay twice during slow response"],
            recommended_action="Hold second payment, initiate refund process  requires human review",
            expected_recovery=s5_total,
            risk_level="high",
            auto_executable=False,
            requires_approval=True,
            policy_result="REVIEW",
            ai_explanation="Two captures for identical order/amount within 3 minutes strongly indicates accidental double-charge. Refund of second payment is appropriate but requires compliance review before execution.",
            created_at=ago(hours=2, minutes=50),
        ))

        # SCENARIO 6  High-value risky action (35,000+ refund)
        s6_cid = customer_ids[4]
        s6_items = [{"product_id": product_ids[5], "name": PRODUCTS_DATA[5]["name"], "qty": 1, "price": PRODUCTS_DATA[5]["price"]}]
        s6_total = PRODUCTS_DATA[5]["price"]  # 1,49,990 Dell XPS
        s6_oid = uid()
        s6_pid = uid()
        s6_incident_id = uid()
        db.add(Order(id=s6_oid, customer_id=s6_cid, status=OrderStatus.FAILED,
                     total_amount=s6_total, items=s6_items, created_at=ago(days=1)))
        db.add(Payment(id=s6_pid, order_id=s6_oid, customer_id=s6_cid,
                       amount=s6_total, method=PaymentMethod.NETBANKING,
                       status=PaymentStatus.FAILED,
                       failure_reason=FailureReason.BANK_DECLINE,
                       failure_message="Bank declined due to risk rules on high-value transaction",
                       gateway_payment_id=f"rzp_sim_{s6_pid[:8]}",
                       attempt_count=2,
                       created_at=ago(days=1),
                       failed_at=ago(days=1)))
        db.add(Incident(
            id=s6_incident_id, type=IncidentType.PAYMENT_FAILED,
            severity=IncidentSeverity.CRITICAL, status=IncidentStatus.ACTION_REQUIRED,
            customer_id=s6_cid, order_id=s6_oid, payment_id=s6_pid,
            amount_at_risk=s6_total,
            root_cause="Bank declined 1,49,990 high-value netbanking transaction due to risk rules. Customer attempted twice.",
            confidence_score=0.86,
            evidence=["Transaction value 1,49,990 exceeds typical daily netbanking limit",
                      "Bank response: HIGH_VALUE_RISK_DECLINE", "2 failed attempts same day",
                      "Customer is Platinum tier  historically completes high-value orders"],
            recommended_action="Offer EMI with 0% interest (6/12 months) or Part-payment option",
            expected_recovery=s6_total,
            risk_level="high",
            auto_executable=False,
            requires_approval=True,
            policy_result="REVIEW",
            ai_explanation="High-value transaction (1,49,990) requires human approval before any recovery action. AI recommends EMI offer but policy mandates review for orders above 50,000.",
            created_at=ago(days=1),
        ))

        await db.commit()
        print("   6 demo scenarios seeded")

        #  4. More abandoned carts 
        print(" Seeding abandoned carts ")
        for i in range(30):
            cid = random.choice(customer_ids)
            n_items = random.randint(1, 4)
            items = []
            total = 0.0
            for _ in range(n_items):
                pid = random.choice(product_ids)
                p = products_map[pid]
                qty = random.randint(1, 2)
                items.append({"product_id": pid, "name": p.name, "qty": qty, "price": p.price})
                total += p.price * qty
            total = round(total, 2)
            intent = round(random.uniform(0.3, 0.95), 2)
            conv_prob = round(random.uniform(0.2, 0.85), 2)
            db.add(Cart(
                id=uid(), customer_id=cid, status=CartStatus.ABANDONED,
                items=items, total_value=total, item_count=n_items,
                intent_score=intent, conversion_probability=conv_prob,
                recommended_intervention=random.choice(INTERVENTIONS),
                expected_recovery=round(total * conv_prob),
                abandoned_at=ago(hours=random.randint(1, 48)),
                created_at=ago(hours=random.randint(49, 72)),
            ))
        await db.commit()
        print("   30 additional abandoned carts")

        #  5. Audit logs 
        print(" Seeding audit logs ")
        agents = ["PaymentInvestigationAgent", "RecoveryAgent", "PolicyAgent",
                  "CustomerIntentAgent", "CommerceAgent", "IncidentManager", "AnalyticsAgent"]
        policies = ["ALLOW", "ALLOW", "ALLOW", "REVIEW", "BLOCK"]
        actions_pool = [
            "Sent recovery email to customer",
            "Initiated webhook replay (simulated)",
            "Triggered alternate payment method suggestion",
            "Flagged duplicate transaction for review",
            "Calculated conversion probability for abandoned cart",
            "Evaluated action safety policy",
            "Generated incident report",
            "Updated incident status to RESOLVED",
            "Sent personalized discount notification",
            "Analyzed payment failure pattern",
        ]
        for _ in range(60):
            db.add(AuditLog(
                id=uid(),
                timestamp=ago(hours=random.randint(0, 168)),
                agent=random.choice(agents),
                incident_id=random.choice([s2_incident_id, s3_incident_id, s4_incident_id, s5_incident_id, s6_incident_id, None]),
                observation=f"Observed payment event with {random.randint(1,5)} anomaly signals",
                decision=random.choice(["Recommend retry", "Flag for review", "Auto-resolve", "Escalate to human", "Send notification"]),
                action=random.choice(actions_pool),
                policy_result=random.choice(policies),
                result=random.choice(["Success", "Pending", "Failed", "Escalated"]),
                confidence=round(random.uniform(0.7, 0.98), 2),
            ))
        await db.commit()
        print("   60 audit log entries")

    print("\n Seeding complete!")
    print("   Products:  ", len(PRODUCTS_DATA))
    print("   Customers: 100")
    print("   Orders:    ~126")
    print("   Payments:  ~130")
    print("   Incidents:  5 demo + ~20 auto")
    print("   Carts:      31 abandoned")
    print("   Audit logs: 60")


if __name__ == "__main__":
    asyncio.run(seed())
