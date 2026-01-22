import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';
import '../models/message.dart';
import '../services/api_service.dart';
import '../services/session_service.dart';
import '../services/storage_service.dart';
import '../services/logging_service.dart';

class ChatProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  final SessionService _sessionService = SessionService();

  List<Message> _messages = [];
  bool _isLoading = false;
  String? _error;
  double? _balance;

  List<Message> get messages => _messages;
  bool get isLoading => _isLoading;
  String? get error => _error;
  double? get balance => _balance;

  String? get userId => _sessionService.currentSession?.userId;
  String? get sessionId => _sessionService.currentSession?.sessionId;

  /// Initialize chat
  Future<void> initialize() async {
    logger.info('Initializing ChatProvider', source: 'ChatProvider');
    await _sessionService.getOrCreateSession();
    logger.info(
      'Session created/retrieved',
      source: 'ChatProvider',
      data: {'sessionId': sessionId, 'userId': userId},
    );

    // Clear previous messages on app load (fresh start)
    await StorageService.clearMessages();
    _messages = [];
    logger.info(
      'Chat cleared on initialize',
      source: 'ChatProvider',
      data: {'messageCount': 0},
    );
    notifyListeners();
  }

  /// Send user message
  Future<void> sendMessage(String text) async {
    if (text.trim().isEmpty) {
      logger.warning(
        'Message send rejected',
        source: 'ChatProvider',
        data: {'reason': 'empty message'},
      );
      return;
    }

    // If no active session, create one (e.g., after clear chat)
    if (sessionId == null || sessionId!.isEmpty) {
      logger.info(
        'No active session, creating new one',
        source: 'ChatProvider',
      );
      await _sessionService.getOrCreateSession();
      notifyListeners();
    }

    // Check if we have a session now
    if (sessionId == null || sessionId!.isEmpty) {
      logger.warning('Failed to create session', source: 'ChatProvider');
      _error = 'Failed to create session';
      notifyListeners();
      return;
    }

    logger.info(
      'Sending user message',
      source: 'ChatProvider',
      data: {'messageLength': text.length, 'sessionId': sessionId},
    );

    // Add user message immediately (optimistic UI)
    final userMessage = Message(
      id: const Uuid().v4(),
      text: text,
      sender: MessageSender.user,
      timestamp: DateTime.now(),
    );

    _messages.add(userMessage);
    _error = null;
    notifyListeners();

    // Save to storage
    StorageService.saveMessages(_messages);

    // Show loading
    _isLoading = true;
    notifyListeners();

    try {
      // Call API
      logger.debug(
        'Making API call to backend',
        source: 'ChatProvider',
        data: {'endpoint': '/api/chat', 'userId': userId},
      );

      final response = await _apiService.sendMessage(
        sessionId: sessionId!,
        userId: userId,
        message: text,
      );

      logger.info(
        'Received API response',
        source: 'ChatProvider',
        data: {
          'responseLength': response.response.length,
          'userId': response.userId,
        },
      );

      // Add bot response
      final botMessage = Message(
        id: const Uuid().v4(),
        text: response.response,
        sender: MessageSender.bot,
        timestamp: DateTime.now(),
        receipt: response.receipt,
      );

      _messages.add(botMessage);

      // Update user ID if provided (after account creation)
      if (response.userId != null && userId == null) {
        logger.info(
          'User ID received from API',
          source: 'ChatProvider',
          data: {'newUserId': response.userId},
        );
        await _sessionService.updateUserId(response.userId!);
      }

      // Update balance if provided
      if (response.balance != null) {
        logger.info(
          'Balance updated',
          source: 'ChatProvider',
          data: {'newBalance': response.balance},
        );
        _balance = response.balance;
      }

      // Save to storage
      StorageService.saveMessages(_messages);
    } catch (e, stackTrace) {
      logger.error(
        'Error sending message: $e',
        source: 'ChatProvider',
        stackTrace: stackTrace,
        data: {'sessionId': sessionId},
      );
      _error = e.toString();

      // Add error message
      final errorMessage = Message(
        id: const Uuid().v4(),
        text: 'Sorry, I encountered an error. Please try again.',
        sender: MessageSender.bot,
        timestamp: DateTime.now(),
        isError: true,
      );

      _messages.add(errorMessage);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Fetch balance
  Future<void> fetchBalance() async {
    if (userId == null) {
      logger.warning(
        'Cannot fetch balance without userId',
        source: 'ChatProvider',
      );
      return;
    }

    logger.info(
      'Fetching balance',
      source: 'ChatProvider',
      data: {'userId': userId},
    );

    try {
      final response = await _apiService.getBalance(userId!);
      _balance = response['balance']?.toDouble();
      logger.info(
        'Balance fetched successfully',
        source: 'ChatProvider',
        data: {'balance': _balance},
      );
      notifyListeners();
    } catch (e, stackTrace) {
      logger.error(
        'Error fetching balance: $e',
        source: 'ChatProvider',
        stackTrace: stackTrace,
        data: {'userId': userId},
      );
    }
  }

  /// Clear chat
  Future<void> clearChat() async {
    logger.info(
      'Clearing chat',
      source: 'ChatProvider',
      data: {'messageCount': _messages.length, 'sessionId': sessionId},
    );

    // Clear frontend state
    _messages.clear();
    _error = null;
    _balance = null;

    // Clear backend session (reset all state including intent locks)
    if (sessionId != null && sessionId!.isNotEmpty) {
      try {
        await _apiService.deleteSession(sessionId!);
        logger.info(
          'Backend session cleared',
          source: 'ChatProvider',
          data: {'sessionId': sessionId},
        );
      } catch (e) {
        logger.error(
          'Error clearing backend session',
          source: 'ChatProvider',
          data: {'error': e.toString()},
        );
      }
    }

    // Clear local storage
    await StorageService.clearSession();

    notifyListeners();
  }

  /// Add message (for testing or special cases)
  void addMessage(Message message) {
    logger.debug(
      'Adding message',
      source: 'ChatProvider',
      data: {
        'sender': message.sender.toString(),
        'messageLength': message.text.length,
      },
    );
    _messages.add(message);
    StorageService.saveMessages(_messages);
    notifyListeners();
  }
}
