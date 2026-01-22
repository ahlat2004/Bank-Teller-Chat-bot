import 'dart:async';
import 'dart:io';
import 'package:intl/intl.dart';
import 'package:path_provider/path_provider.dart';

enum LogLevel {
  debug('DEBUG'),
  info('INFO'),
  warning('WARNING'),
  error('ERROR'),
  critical('CRITICAL');

  final String name;
  const LogLevel(this.name);
}

class LogEntry {
  final DateTime timestamp;
  final LogLevel level;
  final String message;
  final String? source;
  final Map<String, dynamic>? data;
  final StackTrace? stackTrace;

  LogEntry({
    required this.timestamp,
    required this.level,
    required this.message,
    this.source,
    this.data,
    this.stackTrace,
  });

  String toFormattedString() {
    final formatter = DateFormat('yyyy-MM-dd HH:mm:ss.SSS');
    final timestamp = formatter.format(this.timestamp);
    final sourceStr = source != null ? '[$source]' : '';
    final dataStr = data != null ? ' | ${_formatData(data!)}' : '';
    final stackTraceStr = stackTrace != null
        ? '\n${stackTrace.toString()}'
        : '';

    return '$timestamp [${level.name}] $sourceStr $message$dataStr$stackTraceStr';
  }

  static String _formatData(Map<String, dynamic> data) {
    final entries = data.entries
        .map((e) => '${e.key}=${_formatValue(e.value)}')
        .join(', ');
    return '{$entries}';
  }

  static String _formatValue(dynamic value) {
    if (value == null) return 'null';
    if (value is String) {
      return value.length > 100 ? '${value.substring(0, 100)}...' : value;
    }
    if (value is Map || value is List) {
      return value.toString().length > 100
          ? '${value.toString().substring(0, 100)}...'
          : value.toString();
    }
    return value.toString();
  }
}

class LoggingService {
  static final LoggingService _instance = LoggingService._internal();

  factory LoggingService() {
    return _instance;
  }

  LoggingService._internal();

  final List<LogEntry> _logs = [];
  File? _logFile;
  IOSink? _fileSink;
  final StreamController<LogEntry> _logStream =
      StreamController<LogEntry>.broadcast();

  static const int maxLogsInMemory = 1000;
  static const String logFileName = 'bank_chatbot_app.log';

  /// Initialize logging service
  Future<void> initialize() async {
    try {
      final logDir = await _getLogDirectory();
      _logFile = File('${logDir.path}/$logFileName');

      // Clear old log if larger than 5MB
      if (await _logFile!.exists()) {
        final size = await _logFile!.length();
        if (size > 5 * 1024 * 1024) {
          // Backup old log
          final timestamp = DateFormat(
            'yyyyMMdd_HHmmss',
          ).format(DateTime.now());
          final backupFile = File(
            '${logDir.path}/${logFileName.split('.').first}_$timestamp.log',
          );
          await _logFile!.rename(backupFile.path);
          _logFile = File('${logDir.path}/$logFileName');
        }
      }

      // Open file for appending
      final sink = _logFile!.openWrite(mode: FileMode.append);
      _fileSink = sink;

      _log(
        LogEntry(
          timestamp: DateTime.now(),
          level: LogLevel.info,
          message: 'Logging service initialized',
          source: 'LoggingService',
          data: {'logFile': _logFile!.path},
        ),
      );

      print('📝 Logs will be saved to: ${_logFile!.path}');
    } catch (e) {
      print('❌ Failed to initialize logging: $e');
    }
  }

  /// Log debug message
  void debug(String message, {String? source, Map<String, dynamic>? data}) {
    _logMessage(LogLevel.debug, message, source, data);
  }

  /// Log info message
  void info(String message, {String? source, Map<String, dynamic>? data}) {
    _logMessage(LogLevel.info, message, source, data);
  }

  /// Log warning message
  void warning(String message, {String? source, Map<String, dynamic>? data}) {
    _logMessage(LogLevel.warning, message, source, data);
  }

  /// Log error message
  void error(
    String message, {
    String? source,
    Map<String, dynamic>? data,
    StackTrace? stackTrace,
  }) {
    _logMessage(LogLevel.error, message, source, data, stackTrace);
  }

  /// Log critical error
  void critical(
    String message, {
    String? source,
    Map<String, dynamic>? data,
    StackTrace? stackTrace,
  }) {
    _logMessage(LogLevel.critical, message, source, data, stackTrace);
  }

  void _logMessage(
    LogLevel level,
    String message,
    String? source,
    Map<String, dynamic>? data, [
    StackTrace? stackTrace,
  ]) {
    final entry = LogEntry(
      timestamp: DateTime.now(),
      level: level,
      message: message,
      source: source ?? 'App',
      data: data,
      stackTrace: stackTrace,
    );

    _log(entry);
  }

  void _log(LogEntry entry) {
    // Add to in-memory list (with max size)
    _logs.add(entry);
    if (_logs.length > maxLogsInMemory) {
      _logs.removeAt(0);
    }

    // Write to file
    if (_fileSink != null) {
      _fileSink!.write('${entry.toFormattedString()}\n');
    }

    // Print to console in development
    print(entry.toFormattedString());

    // Broadcast to listeners
    _logStream.add(entry);
  }

  /// Get all logs
  List<LogEntry> getAllLogs() => List.from(_logs);

  /// Get logs by level
  List<LogEntry> getLogsByLevel(LogLevel level) {
    return _logs.where((log) => log.level == level).toList();
  }

  /// Get logs since timestamp
  List<LogEntry> getLogsSince(DateTime since) {
    return _logs.where((log) => log.timestamp.isAfter(since)).toList();
  }

  /// Get logs as formatted string
  String getLogsAsString({LogLevel? minLevel}) {
    final filtered = minLevel != null
        ? _logs.where((log) => log.level.index >= minLevel.index).toList()
        : _logs;

    return filtered.map((log) => log.toFormattedString()).join('\n');
  }

  /// Export logs to file
  Future<File?> exportLogs({LogLevel? minLevel}) async {
    try {
      final logDir = await _getLogDirectory();
      final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
      final exportFile = File('${logDir.path}/logs_export_$timestamp.log');

      final content = getLogsAsString(minLevel: minLevel);
      await exportFile.writeAsString(content);

      info(
        'Logs exported successfully',
        source: 'LoggingService',
        data: {'file': exportFile.path},
      );
      return exportFile;
    } catch (e) {
      error('Failed to export logs: $e', source: 'LoggingService');
      return null;
    }
  }

  /// Clear logs
  void clearLogs() {
    _logs.clear();
    info('Logs cleared', source: 'LoggingService');
  }

  /// Get log stream
  Stream<LogEntry> getLogStream() => _logStream.stream;

  /// Get log file path
  Future<String> getLogFilePath() async {
    if (_logFile != null) {
      return _logFile!.path;
    }
    return (await _getLogDirectory()).path;
  }

  /// Close logging
  Future<void> close() async {
    try {
      info('Closing logging service', source: 'LoggingService');
      await _fileSink?.close();
      _logStream.close();
    } catch (e) {
      print('Error closing logging: $e');
    }
  }

  /// Get log directory
  Future<Directory> _getLogDirectory() async {
    late Directory logDir;

    if (Platform.isWindows) {
      // Windows: Use AppData/Local
      final appData =
          Platform.environment['APPDATA'] ??
          Platform.environment['LOCALAPPDATA'];
      logDir = Directory('$appData/BankTellerChatbot/logs');
    } else if (Platform.isMacOS || Platform.isLinux) {
      // macOS/Linux: Use home/.config
      final home = Platform.environment['HOME'];
      logDir = Directory('$home/.config/BankTellerChatbot/logs');
    } else {
      // Fallback: Use documents or temp
      logDir = Directory((await getApplicationDocumentsDirectory()).path);
    }

    if (!logDir.existsSync()) {
      logDir.createSync(recursive: true);
    }

    return logDir;
  }
}

/// Global logging instance
final logger = LoggingService();
