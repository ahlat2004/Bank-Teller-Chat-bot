import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';

class ReceiptCard extends StatefulWidget {
  final Map<String, dynamic> receipt;

  const ReceiptCard({super.key, required this.receipt});

  @override
  State<ReceiptCard> createState() => _ReceiptCardState();
}

class _ReceiptCardState extends State<ReceiptCard> {
  bool _isExpanded = true;

  @override
  Widget build(BuildContext context) {
    final type =
        widget.receipt['type'] ?? widget.receipt['transaction_type'] ?? '';
    final colors = _getColors(type);

    return Container(
      constraints: const BoxConstraints(maxWidth: 400),
      child: Card(
        color: colors['bg'],
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: colors['border']!),
        ),
        child: Column(
          children: [_buildHeader(colors), if (_isExpanded) _buildContent()],
        ),
      ),
    );
  }

  Widget _buildHeader(Map<String, Color> colors) {
    return InkWell(
      onTap: () => setState(() => _isExpanded = !_isExpanded),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.check_circle, color: colors['icon'], size: 20),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                widget.receipt['title'] ?? 'Transaction Receipt',
                style: const TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 15,
                ),
              ),
            ),
            Icon(
              _isExpanded ? Icons.expand_less : Icons.expand_more,
              color: Colors.grey[600],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContent() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Divider(height: 1),
          const SizedBox(height: 16),
          ..._buildFields(),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _copyReceipt,
                  icon: const Icon(Icons.copy, size: 16),
                  label: const Text('Copy'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  List<Widget> _buildFields() {
    final fields = <Widget>[];

    if (widget.receipt['transaction_id'] != null) {
      fields.add(
        _buildField('Transaction ID', widget.receipt['transaction_id']),
      );
    }
    if (widget.receipt['from_account'] != null) {
      fields.add(
        _buildField(
          'From Account',
          _maskAccount(widget.receipt['from_account']),
        ),
      );
    }
    if (widget.receipt['to_account'] != null) {
      fields.add(
        _buildField('To Account', _maskAccount(widget.receipt['to_account'])),
      );
    }
    if (widget.receipt['recipient_name'] != null) {
      fields.add(_buildField('Recipient', widget.receipt['recipient_name']));
    }
    if (widget.receipt['bill_type'] != null) {
      fields.add(_buildField('Bill Type', widget.receipt['bill_type']));
    }
    if (widget.receipt['account_number'] != null) {
      fields.add(
        _buildField(
          'Account Number',
          _maskAccount(widget.receipt['account_number']),
        ),
      );
    }
    if (widget.receipt['account_type'] != null) {
      fields.add(_buildField('Account Type', widget.receipt['account_type']));
    }
    if (widget.receipt['amount'] != null) {
      fields.add(const SizedBox(height: 8));
      fields.add(_buildAmountField('Amount', widget.receipt['amount']));
    }
    if (widget.receipt['new_balance'] != null) {
      fields.add(
        _buildField(
          'New Balance',
          _formatCurrency(widget.receipt['new_balance']),
        ),
      );
    }
    if (widget.receipt['timestamp'] != null) {
      fields.add(const SizedBox(height: 8));
      fields.add(_buildField('Date', _formatDate(widget.receipt['timestamp'])));
    }

    return fields;
  }

  Widget _buildField(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontSize: 13, color: Colors.grey[600])),
          Flexible(
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAmountField(String label, dynamic amount) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(
        border: Border(
          top: BorderSide(color: Colors.grey[200]!),
          bottom: BorderSide(color: Colors.grey[200]!),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
          ),
          Text(
            _formatCurrency(amount),
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  String _maskAccount(dynamic account) {
    final str = account.toString();
    if (str.length <= 4) return str;
    return '****${str.substring(str.length - 4)}';
  }

  String _formatCurrency(dynamic amount) {
    final formatter = NumberFormat.currency(symbol: 'PKR ', decimalDigits: 2);
    return formatter.format(amount);
  }

  String _formatDate(String timestamp) {
    final date = DateTime.parse(timestamp);
    return DateFormat('MMM d, y h:mm a').format(date);
  }

  Map<String, Color> _getColors(String type) {
    switch (type.toLowerCase()) {
      case 'transfer':
        return {
          'bg': Colors.green[50]!,
          'border': Colors.green[200]!,
          'icon': Colors.green[600]!,
        };
      case 'bill_payment':
        return {
          'bg': Colors.blue[50]!,
          'border': Colors.blue[200]!,
          'icon': Colors.blue[600]!,
        };
      case 'account_creation':
        return {
          'bg': Colors.purple[50]!,
          'border': Colors.purple[200]!,
          'icon': Colors.purple[600]!,
        };
      default:
        return {
          'bg': Colors.grey[50]!,
          'border': Colors.grey[200]!,
          'icon': Colors.grey[600]!,
        };
    }
  }

  void _copyReceipt() {
    final text = widget.receipt.toString();
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Receipt copied to clipboard'),
        duration: Duration(seconds: 2),
      ),
    );
  }
}
