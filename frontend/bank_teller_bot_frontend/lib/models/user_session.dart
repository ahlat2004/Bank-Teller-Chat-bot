class UserSession {
  final String sessionId;
  final String? userId;
  final DateTime createdAt;

  UserSession({required this.sessionId, this.userId, required this.createdAt});

  factory UserSession.fromJson(Map<String, dynamic> json) {
    return UserSession(
      sessionId: json['sessionId'] ?? '',
      userId: json['userId'],
      createdAt: DateTime.parse(json['createdAt']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'sessionId': sessionId,
      'userId': userId,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  UserSession copyWith({
    String? sessionId,
    String? userId,
    DateTime? createdAt,
  }) {
    return UserSession(
      sessionId: sessionId ?? this.sessionId,
      userId: userId ?? this.userId,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  static String generateSessionId() {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final random = DateTime.now().microsecondsSinceEpoch % 1000000;
    return 'session_${timestamp}_$random';
  }
}
