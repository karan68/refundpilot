export const RISK_THRESHOLDS = {
  AUTO_APPROVE: 30,
  INVESTIGATE: 70,
  // Above 70 = ESCALATE
};

export const DECISION_COLORS = {
  AUTO_APPROVE: { bg: 'bg-green-500/10', border: 'border-green-500', text: 'text-green-400', label: 'Auto-Approved ⚡' },
  INVESTIGATE: { bg: 'bg-yellow-500/10', border: 'border-yellow-500', text: 'text-yellow-400', label: 'Investigating 🔍' },
  ESCALATE: { bg: 'bg-red-500/10', border: 'border-red-500', text: 'text-red-400', label: 'Escalated 🚩' },
};

export const REFUND_REASONS = [
  { value: 'damaged_in_transit', label: 'Damaged in Transit' },
  { value: 'wrong_product', label: 'Wrong Product Received' },
  { value: 'defective', label: 'Defective Product' },
  { value: 'not_as_described', label: 'Not as Described' },
  { value: 'size_issue', label: 'Size/Fit Issue' },
  { value: 'not_delivered', label: 'Not Delivered' },
  { value: 'changed_mind', label: 'Changed Mind' },
  { value: 'other', label: 'Other' },
];

export const CUSTOMER_PRESETS = [
  { id: 'CUST-001', name: 'Priya Sharma', type: 'loyal', label: '🟢 Priya (Loyal Customer)' },
  { id: 'CUST-002', name: 'Rohit Mehta', type: 'abuser', label: '🔴 Rohit (Serial Abuser)' },
  { id: 'CUST-003', name: 'Anita Verma', type: 'loyal', label: '🟢 Anita (Loyal)' },
  { id: 'CUST-004', name: 'Vikram Singh', type: 'suspect', label: '🟡 Vikram (Suspect)' },
  { id: 'CUST-005', name: 'Meera Patel', type: 'loyal', label: '🟢 Meera (Perfect Record)' },
  { id: 'CUST-006', name: 'Arjun Reddy', type: 'abuser', label: '🔴 Arjun (Serial Abuser)' },
  { id: 'CUST-007', name: 'Neha Gupta', type: 'new', label: '🆕 Neha (New Customer)' },
  { id: 'CUST-008', name: 'Deepak Kumar', type: 'ring', label: '🔵 Deepak (Fraud Ring)' },
  { id: 'CUST-009', name: 'Sunita Devi', type: 'ring', label: '🔵 Sunita (Fraud Ring)' },
];

export const ORDER_PRESETS = {
  'CUST-001': { order_id: 'ORD-1001', product: 'Cotton Kurta - Blue', amount: 800 },
  'CUST-002': { order_id: 'ORD-2001', product: 'Running Shoes - Black', amount: 2400 },
  'CUST-003': { order_id: 'ORD-3001', product: 'Wireless Earbuds Pro', amount: 3500 },
  'CUST-004': { order_id: 'ORD-4001', product: 'Running Shoes - Black', amount: 2400 },
  'CUST-005': { order_id: 'ORD-5001', product: 'Cotton Kurta - Blue', amount: 800 },
  'CUST-006': { order_id: 'ORD-6001', product: 'Wireless Earbuds Pro', amount: 3500 },
  'CUST-007': { order_id: 'ORD-7001', product: 'Wireless Earbuds Pro', amount: 3500 },
  'CUST-008': { order_id: 'ORD-8002', product: 'Running Shoes - Black', amount: 2400 },
  'CUST-009': { order_id: 'ORD-9002', product: 'Ceramic Vase - White', amount: 1200 },
};
