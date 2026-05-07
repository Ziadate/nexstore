from flask import Blueprint, request, jsonify

chatbot_bp = Blueprint('chatbot', __name__)

RESPONSES = {
    # تحيات
    "مرحبا":        "أهلاً بك في NexStore! 😊 كيف أقدر أساعدك؟",
    "اهلا":         "أهلاً وسهلاً! 😊 كيف أقدر أساعدك؟",
    "هاي":          "أهلاً بك! 😊 كيف أقدر أساعدك؟",
    "hello":        "Welcome to NexStore! 😊 How can I help you?",
    "hi":           "Hi there! 😊 How can I help you?",
    "hey":          "Hey! 😊 How can I help you?",

    # منتجات
    "منتج":         "عندنا: 📱 موبايلات، 💻 لابتوبات، 🎧 سماعات، 👗 ملابس، 🏠 أجهزة منزلية، 🎮 العاب!",
    "المنتجات":     "عندنا: 📱 موبايلات، 💻 لابتوبات، 🎧 سماعات، 👗 ملابس، 🏠 أجهزة منزلية، 🎮 العاب!",
    "products":     "We have: 📱 Phones, 💻 Laptops, 🎧 Headphones, 👗 Fashion, 🏠 Home Appliances, 🎮 Gaming!",
    "موبايل":       "عندنا أحدث الموبايلات! 📱 iPhone, Samsung, وأكتر. تفضل تصفح قسم الموبايلات!",
    "phone":        "We have the latest phones! 📱 iPhone, Samsung & more. Browse our Phones section!",
    "لابتوب":       "عندنا لابتوبات للجميع! 💻 MacBook, Dell, HP وأكتر. تفضل تصفح قسم اللابتوبات!",
    "laptop":       "We have laptops for everyone! 💻 MacBook, Dell, HP & more.",
    "سماعات":       "عندنا أفضل السماعات! 🎧 Sony, Bose, Apple AirPods وأكتر.",
    "headphone":    "We have the best headphones! 🎧 Sony, Bose, Apple AirPods & more.",
    "gaming":       "Check our gaming section! 🎮 PS5, Xbox, Nintendo & accessories.",
    "العاب":        "عندنا قسم ألعاب رائع! 🎮 PS5, Xbox, Nintendo وإكسسوارات.",

    # أسعار
    "سعر":          "الأسعار بتبدأ من $199 لحد $2499! 💰 تفضل تصفح الموقع لشوف كل الأسعار.",
    "كم":           "الأسعار بتبدأ من $199 لحد $2499! 💰 تفضل تصفح الموقع لشوف كل الأسعار.",
    "بكام":         "الأسعار بتبدأ من $199 لحد $2499! 💰 تفضل تصفح الموقع لشوف كل الأسعار.",
    "price":        "Prices start from $199 up to $2499! 💰 Browse our site to see all prices.",
    "how much":     "Prices start from $199 up to $2499! 💰 Browse our site to see all prices.",

    # خصومات
    "خصم":          "استخدم كود DISCOUNT10 للحصول على خصم 10%! 🎉",
    "كوبون":        "استخدم كود DISCOUNT10 للحصول على خصم 10%! 🎉",
    "كود":          "استخدم كود DISCOUNT10 للحصول على خصم 10%! 🎉",
    "discount":     "Use code DISCOUNT10 to get 10% off! 🎉",
    "coupon":       "Use code DISCOUNT10 to get 10% off! 🎉",
    "offer":        "Use code DISCOUNT10 to get 10% off! 🎉",
    "عروض":         "استخدم كود DISCOUNT10 للحصول على خصم 10%! 🎉 وشوف المنتجات المميزة على الصفحة الرئيسية.",

    # شحن وتوصيل
    "شحن":          "التوصيل خلال 3-5 أيام عمل. 🚚 الشحن مجاني على الطلبات فوق $500!",
    "توصيل":        "التوصيل خلال 3-5 أيام عمل. 🚚 الشحن مجاني على الطلبات فوق $500!",
    "shipping":     "Delivery within 3-5 business days. 🚚 Free shipping on orders over $500!",
    "delivery":     "Delivery within 3-5 business days. 🚚 Free shipping on orders over $500!",

    # إرجاع
    "رجوع":         "سياسة الإرجاع 14 يوم من تاريخ الاستلام. 🔄 المنتج لازم يكون بحالته الأصلية.",
    "إرجاع":        "سياسة الإرجاع 14 يوم من تاريخ الاستلام. 🔄 المنتج لازم يكون بحالته الأصلية.",
    "استرجاع":      "سياسة الإرجاع 14 يوم من تاريخ الاستلام. 🔄 المنتج لازم يكون بحالته الأصلية.",
    "return":       "Return policy is 14 days from delivery date. 🔄 Item must be in original condition.",
    "refund":       "Refund policy is 14 days from delivery date. 🔄 Item must be in original condition.",

    # دفع
    "دفع":          "طرق الدفع: 💵 كاش عند الاستلام، 💳 كريدت كارد، أو 📱 محفظة إلكترونية.",
    "فلوس":         "طرق الدفع: 💵 كاش عند الاستلام، 💳 كريدت كارد، أو 📱 محفظة إلكترونية.",
    "payment":      "Payment methods: 💵 Cash on delivery, 💳 Credit card, or 📱 Digital wallet.",
    "pay":          "Payment methods: 💵 Cash on delivery, 💳 Credit card, or 📱 Digital wallet.",

    # تواصل
    "تواصل":        "تواصل معنا على: 📧 support@nexstore.com",
    "مساعده":       "أنا هنا لمساعدتك! 😊 تقدر تسأل عن: المنتجات، الأسعار، الشحن، الإرجاع، أو الدفع.",
    "مساعدة":       "أنا هنا لمساعدتك! 😊 تقدر تسأل عن: المنتجات، الأسعار، الشحن، الإرجاع، أو الدفع.",
    "contact":      "Contact us at: 📧 support@nexstore.com",
    "help":         "I'm here to help! 😊 You can ask about: products, prices, shipping, returns, or payment.",

    # طلبات
    "طلب":          "تقدر تتبع طلبك من صفحة الملف الشخصي في 'My Orders'. 📦",
    "order":        "You can track your order from your Profile page under 'My Orders'. 📦",
    "track":        "You can track your order from your Profile page under 'My Orders'. 📦",
}

DEFAULT_AR = "عذراً، مش فاهم سؤالك تماماً. 😊 ممكن تسأل عن:\n• المنتجات والأسعار\n• الشحن والتوصيل\n• الإرجاع والاسترجاع\n• طرق الدفع\n• كود الخصم"
DEFAULT_EN = "Sorry, I didn't quite understand. 😊 You can ask about:\n• Products & prices\n• Shipping & delivery\n• Returns & refunds\n• Payment methods\n• Discount codes"


@chatbot_bp.route('/chatbot', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400

        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        lower_msg = user_message.lower()
        reply = None

        for key, response in RESPONSES.items():
            if key in lower_msg:
                reply = response
                break

        if not reply:
            # تحديد لغة الرسالة
            is_arabic = any(ord(c) > 127 for c in user_message)
            reply = DEFAULT_AR if is_arabic else DEFAULT_EN

        return jsonify({'response': reply, 'status': 'success'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500