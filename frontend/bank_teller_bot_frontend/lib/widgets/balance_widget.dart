import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../config/theme.dart';

class BalanceWidget extends StatefulWidget {
  final double? balance;
  final VoidCallback onRefresh;

  const BalanceWidget({super.key, this.balance, required this.onRefresh});

  @override
  State<BalanceWidget> createState() => _BalanceWidgetState();
}

class _BalanceWidgetState extends State<BalanceWidget> {
  bool _isVisible = true;
  bool _isRefreshing = false;

  Future<void> _handleRefresh() async {
    setState(() => _isRefreshing = true);
    widget.onRefresh();
    await Future.delayed(const Duration(milliseconds: 500));
    if (mounted) {
      setState(() => _isRefreshing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (widget.balance == null) return const SizedBox.shrink();

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppTheme.primaryBlue, Color(0xFF2563EB)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryBlue.withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(
                    Icons.account_balance_wallet,
                    color: Colors.white,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text('Current Balance', style: AppTheme.balanceLabel),
                ],
              ),
              Row(
                children: [
                  IconButton(
                    icon: Icon(
                      _isVisible ? Icons.visibility_off : Icons.visibility,
                      color: Colors.white,
                      size: 20,
                    ),
                    onPressed: () {
                      setState(() => _isVisible = !_isVisible);
                    },
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: Icon(Icons.refresh, color: Colors.white, size: 20),
                    onPressed: _isRefreshing ? null : _handleRefresh,
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            _isVisible ? _formatCurrency(widget.balance!) : '••••••',
            style: AppTheme.balanceAmount,
          ),
          const SizedBox(height: 4),
          Text(
            'Updated just now',
            style: AppTheme.balanceLabel.copyWith(fontSize: 12),
          ),
        ],
      ),
    );
  }

  String _formatCurrency(double amount) {
    final formatter = NumberFormat.currency(symbol: 'PKR ', decimalDigits: 2);
    return formatter.format(amount);
  }
}
