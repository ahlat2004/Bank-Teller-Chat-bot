import '../models/user_session.dart';
import 'storage_service.dart';

class SessionService {
  UserSession? _currentSession;

  /// Get or create session
  Future<UserSession> getOrCreateSession() async {
    if (_currentSession != null) {
      return _currentSession!;
    }

    // Try to load from storage
    final storedSession = StorageService.getSession();

    if (storedSession != null) {
      _currentSession = storedSession;
      return storedSession;
    }

    // Create new session
    final newSession = UserSession(
      sessionId: UserSession.generateSessionId(),
      createdAt: DateTime.now(),
    );

    await StorageService.saveSession(newSession);
    _currentSession = newSession;

    return newSession;
  }

  /// Update user ID
  Future<void> updateUserId(String userId) async {
    if (_currentSession != null) {
      _currentSession = _currentSession!.copyWith(userId: userId);
      await StorageService.saveSession(_currentSession!);
      await StorageService.updateUserId(userId);
    }
  }

  /// Get current session
  UserSession? get currentSession => _currentSession;

  /// Clear session
  Future<void> clearSession() async {
    _currentSession = null;
    await StorageService.clearSession();
  }

  /// Check if user is logged in
  bool get isLoggedIn => _currentSession?.userId != null;
}
