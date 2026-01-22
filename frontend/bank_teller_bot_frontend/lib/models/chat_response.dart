class ChatResponse {
  final String response;
  final String? message;
  final Map<String, dynamic>? receipt;
  final String? error;
  final String? action;
  final String? userId;
  final double? balance;

  ChatResponse({
    required this.response,
    this.message,
    this.receipt,
    this.error,
    this.action,
    this.userId,
    this.balance,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      response: json['response'] ?? json['message'] ?? '',
      message: json['message'],
      receipt: json['receipt'],
      error: json['error'],
      action: json['action'],
      userId: json['user_id'],
      balance: json['balance']?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'response': response,
      'message': message,
      'receipt': receipt,
      'error': error,
      'action': action,
      'user_id': userId,
      'balance': balance,
    };
  }
}
