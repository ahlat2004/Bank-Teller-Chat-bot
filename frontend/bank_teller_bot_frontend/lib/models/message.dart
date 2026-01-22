class Message {
  final String id;
  final String text;
  final MessageSender sender;
  final DateTime timestamp;
  final Map<String, dynamic>? receipt;
  final bool isError;

  Message({
    required this.id,
    required this.text,
    required this.sender,
    required this.timestamp,
    this.receipt,
    this.isError = false,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'] ?? '',
      text: json['text'] ?? '',
      sender: json['sender'] == 'user' ? MessageSender.user : MessageSender.bot,
      timestamp: DateTime.parse(json['timestamp']),
      receipt: json['receipt'],
      isError: json['isError'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'text': text,
      'sender': sender == MessageSender.user ? 'user' : 'bot',
      'timestamp': timestamp.toIso8601String(),
      'receipt': receipt,
      'isError': isError,
    };
  }

  Message copyWith({
    String? id,
    String? text,
    MessageSender? sender,
    DateTime? timestamp,
    Map<String, dynamic>? receipt,
    bool? isError,
  }) {
    return Message(
      id: id ?? this.id,
      text: text ?? this.text,
      sender: sender ?? this.sender,
      timestamp: timestamp ?? this.timestamp,
      receipt: receipt ?? this.receipt,
      isError: isError ?? this.isError,
    );
  }
}

enum MessageSender { user, bot }
