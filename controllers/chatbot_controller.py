from flask import Blueprint, request, jsonify
import random

chatbot_bp = Blueprint('chatbot', __name__)

# ردود متعددة عشوائية لنفس السؤال
RESPONSES = {
    # تحيات
    ("مرحبا", "هاي", "هلو", "اهلا", "السلام", "صباح", "مساء", "ازيك", "ازيكم", "عامل", "كيفك", "كيف حالك", "hello", "hi", "hey", "good morning", "good evening", "how are you", "howdy"): [
        "اهلاً وسهلاً! 😊 انا NexBot مساعدك في NexStore. كيف اقدر اساعدك النهارده؟",
        "هلا هلا! 👋 يسعدني اساعدك. ايه اللي تحتاجه؟",
        "مرحباً بيك في NexStore! 🎉 احنا هنا عشان نخلي تجربة التسوق بتاعتك مميزة. ايه اللي تحتاجه؟",
        "اهلين! 😄 انا بخير والحمد لله. انت عايز تتسوق ولا عندك استفسار؟",
    ],

    # منتجات
    ("منتجات", "عندكم ايه", "بتبيعوا ايه", "اشتري", "تسوق", "products", "what do you sell", "what do you have"): [
        "عندنا تشكيلة رهيبة! 🛍️\n📱 موبايلات\n💻 لابتوبات\n🎧 سماعات\n👗 ملابس\n🏠 اجهزة منزلية\n🎮 العاب\nادخل على الموقع وتصفح! 😊",
        "NexStore فيها كل حاجة! 🔥 موبايلات، لابتوبات، سماعات، ملابس، اجهزة منزلية وألعاب. ايه اللي بتدور عليه بالظبط؟",
    ],

    # موبايلات
    ("موبايل", "تليفون", "ايفون", "سامسونج", "phone", "iphone", "samsung", "mobile"): [
        "عندنا احدث الموبايلات! 📱\n✨ iPhone 15 Pro Max - $1,299\n✨ Samsung Galaxy S24 Ultra - $1,199\nوكمان في تانيين كتير! تصفح قسم الموبايلات. 😊",
        "قسم الموبايلات عندنا فيه احدث الاصدارات من Apple و Samsung وغيرهم! 📱 الاسعار بتبدأ من $199.",
    ],

    # لابتوب
    ("لابتوب", "كمبيوتر", "ماك", "laptop", "macbook", "computer", "pc"): [
        "عندنا لابتوبات من احسن الماركات! 💻\n✨ MacBook Pro 16 M3 Max - $2,499\nوفي خيارات تانية بأسعار مناسبة. تصفح قسم اللابتوبات! 😊",
        "قسم اللابتوبات فيه MacBook وWindows laptops بأسعار مختلفة! 💻 ايه الميزانية المناسبة ليك؟",
    ],

    # سعر
    ("سعر", "بكام", "كام", "كم", "price", "how much", "cost"): [
        "الاسعار عندنا مناسبة جداً! 💰 بتبدأ من $199 لحد $2,499 حسب المنتج. استخدم كود DISCOUNT10 للحصول على خصم 10%! 🎉",
        "عندنا منتجات لكل الميزانيات! 💸 من $199 للمنتجات الاقتصادية لحد $2,499 للمنتجات البريميوم. ايه الميزانية بتاعتك؟",
    ],

    # خصم وعروض
    ("خصم", "عرض", "اوفر", "كوبون", "discount", "offer", "coupon", "sale", "promo"): [
        "عندنا عروض حلوة! 🎁 استخدم كود DISCOUNT10 عند الدفع وهتاخد خصم 10% على اي منتج! 🔥",
        "اكيد! 😊 كود الخصم هو DISCOUNT10 - هيديك 10% خصم على طلبك. ولا تنسى تتفرج على منتجات SALE على الموقع!",
    ],

    # شحن وتوصيل
    ("شحن", "توصيل", "بيجي امتى", "delivery", "shipping", "when will", "arrive"): [
        "التوصيل خلال 3-5 ايام عمل! 🚚 وبنوصل لكل مكان. هل عندك استفسار عن طلب معين؟",
        "الشحن سريع! 📦 3-5 ايام عمل من تاريخ الطلب. وبنبعتلك رقم تتبع عشان تعرف الطرد فين. 😊",
    ],

    # ارجاع
    ("ارجاع", "استرجاع", "مش عاجبني", "return", "refund", "exchange"): [
        "سياسة الارجاع عندنا سهلة! ↩️ عندك 14 يوم من تاريخ الاستلام ترجع اي منتج. تواصل معانا على support@nexstore.com 😊",
        "مش مشكلة! 😊 عندك 14 يوم ترجع المنتج لو مش عاجبك. بس المنتج يكون في حالته الاصلية. ايه المنتج اللي عايز ترجعه؟",
    ],

    # دفع
    ("دفع", "فلوس", "payment", "pay", "بطاقة", "كاش", "credit", "card", "visa"): [
        "طرق الدفع عندنا متنوعة! 💳\n✅ كاش عند الاستلام\n✅ كريدت/ديبت كارد\n✅ محفظة الكترونية\nكلها امنة 100%! 🔒",
        "بندعم كل طرق الدفع! 💰 كاش، كارت، ومحفظة الكترونية. اختار اللي يناسبك. 😊",
    ],

    # تواصل
    ("تواصل", "contact", "support", "مساعدة", "دعم", "help"): [
        "تقدر تتواصل معانا على 📧 support@nexstore.com - هنرد عليك في اسرع وقت! 😊",
        "خدمة العملاء متاحة دايما! 📞 راسلنا على support@nexstore.com وهنساعدك. 😊",
    ],

    # شكر
    ("شكرا", "تسلم", "ممتاز", "thanks", "thank you", "great", "awesome"): [
        "العفو! 😊 يسعدني اساعدك. في حاجة تانية؟",
        "بكل سرور! 🌟 NexStore دايما في خدمتك. تسوق سعيد! 🛍️",
    ],

    # وداع
    ("مع السلامة", "باي", "goodbye", "bye", "سلام", "تصبح"): [
        "مع السلامة! 👋 يسعدنا زيارتك تاني. تسوق سعيد! 🛍️",
        "الى اللقاء! 😊 ارجع لينا اي وقت. NexStore في خدمتك دايما! 🌟",
    ],
}

DEFAULT_RESPONSES_AR = [
    "مش فاهم قصدك بالظبط 😅 ممكن تسألني عن:\n🛍️ المنتجات\n💰 الاسعار والخصومات\n🚚 الشحن والتوصيل\n↩️ الارجاع\n💳 طرق الدفع",
    "سؤالك وصلني بس محتاج توضيح! 😊 انا اقدر اساعدك في المنتجات، الاسعار، الشحن، الارجاع، وطرق الدفع. ايه اللي تحتاجه؟",
    "هعمل مجهودي اساعدك! 💪 بس ممكن تسألني عن المنتجات، الاسعار، او الطلبات؟",
]

DEFAULT_RESPONSES_EN = [
    "I'm not sure I understand 😅 I can help with:\n🛍️ Products\n💰 Prices & discounts\n🚚 Shipping\n↩️ Returns\n💳 Payment methods",
    "Could you clarify? 😊 I can help with products, prices, shipping, returns, and payment.",
]


def find_response(message):
    message_lower = message.lower().strip()
    for keywords, responses in RESPONSES.items():
        for keyword in keywords:
            if keyword in message_lower:
                return random.choice(responses)
    return None


@chatbot_bp.route('/chatbot', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'No message'}), 400

        reply = find_response(user_message)

        if not reply:
            is_arabic = any(ord(c) > 127 for c in user_message)
            reply = random.choice(DEFAULT_RESPONSES_AR if is_arabic else DEFAULT_RESPONSES_EN)

        return jsonify({'response': reply, 'status': 'success'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500