import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';
import '../models/user_session.dart';
import '../models/message.dart';

class StorageService {
  static SharedPreferences? _prefs;

  /// Initialize storage
  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  /// Save session
  static Future<bool> saveSession(UserSession session) async {
    try {
      await _prefs?.setString(AppConfig.sessionIdKey, session.sessionId);

      if (session.userId != null) {
        await _prefs?.setString(AppConfig.userIdKey, session.userId!);
      }

      return true;
    } catch (e) {
      print('Error saving session: $e');
      return false;
    }
  }

  /// Get session
  static UserSession? getSession() {
    try {
      final sessionId = _prefs?.getString(AppConfig.sessionIdKey);
      final userId = _prefs?.getString(AppConfig.userIdKey);

      if (sessionId != null) {
        return UserSession(
          sessionId: sessionId,
          userId: userId,
          createdAt: DateTime.now(),
        );
      }
      return null;
    } catch (e) {
      print('Error getting session: $e');
      return null;
    }
  }

  /// Update user ID
  static Future<bool> updateUserId(String userId) async {
    try {
      await _prefs?.setString(AppConfig.userIdKey, userId);
      return true;
    } catch (e) {
      print('Error updating user ID: $e');
      return false;
    }
  }

  /// Clear session
  static Future<bool> clearSession() async {
    try {
      await _prefs?.remove(AppConfig.sessionIdKey);
      await _prefs?.remove(AppConfig.userIdKey);
      await _prefs?.remove(AppConfig.messagesKey);
      return true;
    } catch (e) {
      print('Error clearing session: $e');
      return false;
    }
  }

  /// Clear messages only
  static Future<bool> clearMessages() async {
    try {
      await _prefs?.remove(AppConfig.messagesKey);
      return true;
    } catch (e) {
      print('Error clearing messages: $e');
      return false;
    }
  }

  /// Save messages
  static Future<bool> saveMessages(List<Message> messages) async {
    try {
      final jsonList = messages.map((m) => m.toJson()).toList();
      await _prefs?.setString(AppConfig.messagesKey, jsonEncode(jsonList));
      return true;
    } catch (e) {
      print('Error saving messages: $e');
      return false;
    }
  }

  /// Get messages
  static List<Message> getMessages() {
    try {
      final jsonString = _prefs?.getString(AppConfig.messagesKey);
      if (jsonString != null) {
        final jsonList = jsonDecode(jsonString) as List;
        return jsonList.map((json) => Message.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      print('Error getting messages: $e');
      return [];
    }
  }

  /// Clear all data
  static Future<bool> clearAll() async {
    try {
      await _prefs?.clear();
      return true;
    } catch (e) {
      print('Error clearing all data: $e');
      return false;
    }
  }
}
