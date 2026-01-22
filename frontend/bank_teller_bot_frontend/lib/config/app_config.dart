class AppConfig {
  // API Configuration
  static const String apiBaseUrl = 'http://localhost:8000';
  static const Duration apiTimeout = Duration(seconds: 10);

  // App Information
  static const String appName = 'Bank Teller';
  static const String appVersion = '1.0.0';

  // Storage Keys
  static const String sessionIdKey = 'bank_session_id';
  static const String userIdKey = 'bank_user_id';
  static const String messagesKey = 'bank_messages';

  // UI Configuration
  static const int maxMessageLength = 500;
  static const Duration typingIndicatorDelay = Duration(milliseconds: 500);

  // API Endpoints
  static const String chatEndpoint = '/api/chat';
  static const String balanceEndpoint = '/api/balance';
  static const String sendOtpEndpoint = '/api/auth/send-otp';
  static const String verifyOtpEndpoint = '/api/auth/verify-otp';
  static const String checkEmailEndpoint = '/api/auth/check-email';

  // Messages
  static const String welcomeMessage =
      "👋 Welcome to Bank Teller! I'm here to help you with your banking needs.";
  static const String errorGeneric = "Something went wrong. Please try again.";
  static const String errorNetwork =
      "Network error. Please check your connection.";

  // Quick Actions
  static const List<Map<String, dynamic>> quickActions = [
    {'text': 'Create an account', 'icon': 'person_add'},
    {'text': 'Check my balance', 'icon': 'account_balance_wallet'},
    {'text': 'Transfer money', 'icon': 'send'},
    {'text': 'Pay a bill', 'icon': 'receipt'},
    {'text': 'Get help', 'icon': 'help'},
  ];
}
