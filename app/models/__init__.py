from app.core.database import Base

# Импортируем все модели, чтобы create_all видел их
from .user import User
from .region import Region
from .property import Property
from .property_unit import PropertyUnit
from .review import Review
from .tour import Tour, TourStop, UserTourExpense
from .booking import BookingRequest
from .chat import ChatMessage
from .photo import Photo
from .exchange_rate import ExchangeRate
from .saved import SavedItem
from .property_tag import PropertyTag
from .notification import Notification
from .tour_booking import TourBooking
from .promo_code import PromoCode
from .property_hotel import PropertyHotel