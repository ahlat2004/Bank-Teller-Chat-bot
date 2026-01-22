import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'config/theme.dart';
import 'providers/chat_provider.dart';
import 'screens/chat_screen.dart';
import 'screens/splash_screen.dart';
import 'services/storage_service.dart';
import 'services/logging_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize logging first
  await logger.initialize();
  logger.info('Application starting', source: 'main');

  // Initialize storage
  await StorageService.init();
  logger.info('Storage service initialized', source: 'main');

  runApp(const BankTellerApp());
}

class BankTellerApp extends StatelessWidget {
  const BankTellerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [ChangeNotifierProvider(create: (_) => ChatProvider())],
      child: MaterialApp(
        title: 'Bank Teller',
        theme: AppTheme.lightTheme,
        debugShowCheckedModeBanner: false,
        home: const AppInitializer(),
      ),
    );
  }
}

class AppInitializer extends StatefulWidget {
  const AppInitializer({super.key});

  @override
  State<AppInitializer> createState() => _AppInitializerState();
}

class _AppInitializerState extends State<AppInitializer> {
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _initialize();
  }

  Future<void> _initialize() async {
    try {
      logger.info('Initializing chat provider', source: 'AppInitializer');
      // Initialize chat provider
      final chatProvider = Provider.of<ChatProvider>(context, listen: false);
      await chatProvider.initialize();
      logger.info(
        'Chat provider initialized successfully',
        source: 'AppInitializer',
      );

      // Small delay for splash screen
      await Future.delayed(const Duration(seconds: 1));

      if (mounted) {
        setState(() => _isInitialized = true);
      }
    } catch (e, stackTrace) {
      logger.error(
        'Error during initialization: $e',
        source: 'AppInitializer',
        stackTrace: stackTrace,
      );
      if (mounted) {
        setState(() => _isInitialized = true);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return _isInitialized ? const ChatScreen() : const SplashScreen();
  }
}
