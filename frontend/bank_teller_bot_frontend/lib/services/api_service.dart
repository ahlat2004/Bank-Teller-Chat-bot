import 'package:dio/dio.dart';
import '../config/app_config.dart';
import '../models/chat_response.dart';
import 'logging_service.dart';

class ApiService {
  late final Dio _dio;

  ApiService() {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.apiBaseUrl,
        connectTimeout: AppConfig.apiTimeout,
        receiveTimeout: AppConfig.apiTimeout,
        headers: {'Content-Type': 'application/json'},
      ),
    );

    // Add interceptors for logging
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          logger.debug(
            'API Request',
            source: 'ApiService',
            data: {
              'method': options.method,
              'path': options.path,
              'baseUrl': options.baseUrl,
            },
          );
          return handler.next(options);
        },
        onResponse: (response, handler) {
          logger.info(
            'API Response',
            source: 'ApiService',
            data: {
              'statusCode': response.statusCode,
              'path': response.requestOptions.path,
              'contentLength': response.data.toString().length,
            },
          );
          return handler.next(response);
        },
        onError: (error, handler) {
          logger.error(
            'API Error',
            source: 'ApiService',
            stackTrace: error.stackTrace,
            data: {
              'type': error.type.toString(),
              'message': error.message,
              'statusCode': error.response?.statusCode,
              'path': error.requestOptions.path,
            },
          );
          return handler.next(error);
        },
      ),
    );

    logger.info(
      'ApiService initialized',
      source: 'ApiService',
      data: {
        'baseUrl': AppConfig.apiBaseUrl,
        'timeout': AppConfig.apiTimeout.inSeconds,
      },
    );
  }

  /// Send chat message
  Future<ChatResponse> sendMessage({
    required String sessionId,
    dynamic userId,
    required String message,
  }) async {
    try {
      // Convert userId to int or use default
      int parsedUserId = 1;
      if (userId != null) {
        try {
          if (userId is int) {
            parsedUserId = userId;
          } else if (userId is String && userId.isNotEmpty) {
            parsedUserId = int.parse(userId);
          }
        } catch (e) {
          // Keep default
          parsedUserId = 1;
        }
      }

      logger.debug(
        'Sending chat message',
        source: 'ApiService',
        data: {
          'sessionId': sessionId,
          'userId': parsedUserId,
          'messageLength': message.length,
        },
      );

      final response = await _dio.post(
        AppConfig.chatEndpoint,
        data: {
          'message': message,
          'user_id': parsedUserId,
          'session_id': sessionId,
        },
      );

      final chatResponse = ChatResponse.fromJson(response.data);

      logger.info(
        'Chat message response received',
        source: 'ApiService',
        data: {
          'responseLength': chatResponse.response.length,
          'userId': parsedUserId,
        },
      );

      return chatResponse;
    } on DioException catch (e) {
      logger.error(
        'Chat message API error: ${_handleError(e)}',
        source: 'ApiService',
        stackTrace: e.stackTrace,
        data: {'sessionId': sessionId},
      );
      throw _handleError(e);
    }
  }

  /// Get account balance
  Future<Map<String, dynamic>> getBalance(String userId) async {
    try {
      logger.debug(
        'Fetching balance',
        source: 'ApiService',
        data: {'userId': userId},
      );
      final response = await _dio.get('${AppConfig.balanceEndpoint}/$userId');
      logger.info(
        'Balance fetched',
        source: 'ApiService',
        data: {
          'userId': userId,
          'hasBalance': response.data.containsKey('balance'),
        },
      );
      return response.data;
    } on DioException catch (e) {
      logger.error(
        'Balance fetch error: ${_handleError(e)}',
        source: 'ApiService',
        stackTrace: e.stackTrace,
        data: {'userId': userId},
      );
      throw _handleError(e);
    }
  }

  /// Check if email exists
  Future<Map<String, dynamic>> checkEmail(String email) async {
    try {
      logger.debug(
        'Checking email',
        source: 'ApiService',
        data: {'email': email},
      );
      final response = await _dio.get('${AppConfig.checkEmailEndpoint}/$email');
      logger.info(
        'Email check completed',
        source: 'ApiService',
        data: {'email': email},
      );
      return response.data;
    } on DioException catch (e) {
      logger.error(
        'Email check error: ${_handleError(e)}',
        source: 'ApiService',
        stackTrace: e.stackTrace,
        data: {'email': email},
      );
      throw _handleError(e);
    }
  }

  /// Send OTP to email
  Future<Map<String, dynamic>> sendOTP(String email) async {
    try {
      logger.debug('Sending OTP', source: 'ApiService', data: {'email': email});
      final response = await _dio.post(
        AppConfig.sendOtpEndpoint,
        data: {'email': email},
      );
      logger.info(
        'OTP sent successfully',
        source: 'ApiService',
        data: {'email': email},
      );
      return response.data;
    } on DioException catch (e) {
      logger.error(
        'OTP send error: ${_handleError(e)}',
        source: 'ApiService',
        stackTrace: e.stackTrace,
        data: {'email': email},
      );
      throw _handleError(e);
    }
  }

  /// Verify OTP
  Future<Map<String, dynamic>> verifyOTP(String email, String otpCode) async {
    try {
      logger.debug(
        'Verifying OTP',
        source: 'ApiService',
        data: {'email': email},
      );
      final response = await _dio.post(
        AppConfig.verifyOtpEndpoint,
        data: {'email': email, 'otp_code': otpCode},
      );
      logger.info(
        'OTP verified successfully',
        source: 'ApiService',
        data: {'email': email},
      );
      return response.data;
    } on DioException catch (e) {
      logger.error(
        'OTP verify error: ${_handleError(e)}',
        source: 'ApiService',
        stackTrace: e.stackTrace,
        data: {'email': email},
      );
      throw _handleError(e);
    }
  }

  /// Handle Dio errors
  String _handleError(DioException error) {
    if (error.response != null) {
      // Server responded with error
      var message = 'Server error';

      try {
        final data = error.response?.data;
        if (data is Map) {
          message = data['detail'] ?? data['message'] ?? message;
        } else if (data is String) {
          message = data;
        } else if (data is List) {
          message = 'Validation error in request';
        }
      } catch (e) {
        logger.debug('Error parsing response data: $e', source: 'ApiService');
      }

      return message.toString();
    } else if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return 'Connection timeout. Please try again.';
    } else if (error.type == DioExceptionType.connectionError) {
      return 'Network error. Please check your connection.';
    } else {
      return 'Something went wrong. Please try again.';
    }
  }

  /// Delete session (clear chat state on backend)
  Future<void> deleteSession(String sessionId) async {
    try {
      logger.debug(
        'Deleting session',
        source: 'ApiService',
        data: {'sessionId': sessionId},
      );

      await _dio.delete('/api/session/$sessionId');

      logger.debug(
        'Session deleted',
        source: 'ApiService',
        data: {'sessionId': sessionId},
      );
    } on DioException catch (e) {
      logger.error(
        'Failed to delete session',
        source: 'ApiService',
        data: {'sessionId': sessionId, 'error': _handleError(e)},
      );
      rethrow;
    }
  }
}
