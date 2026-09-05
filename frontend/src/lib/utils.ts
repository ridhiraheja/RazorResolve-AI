export function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ')
}

export function formatINR(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function timeAgo(iso: string | null | undefined): string {
  if (!iso) return '—'
  const diff = (Date.now() - new Date(iso).getTime()) / 1000
  if (diff < 60) return `${Math.floor(diff)}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

export function confidenceLabel(score: number): string {
  if (score >= 0.9) return 'Very High'
  if (score >= 0.8) return 'High'
  if (score >= 0.7) return 'Moderate'
  return 'Low'
}

export function severityColor(severity: string) {
  switch (severity) {
    case 'critical': return 'text-red-700 bg-red-50 border-red-200'
    case 'high':     return 'text-orange-700 bg-orange-50 border-orange-200'
    case 'medium':   return 'text-yellow-700 bg-yellow-50 border-yellow-200'
    default:         return 'text-green-700 bg-green-50 border-green-200'
  }
}

export function statusColor(status: string) {
  switch (status) {
    case 'new':             return 'bg-blue-100 text-blue-800'
    case 'investigating':   return 'bg-yellow-100 text-yellow-800'
    case 'action_required': return 'bg-orange-100 text-orange-800'
    case 'recovering':      return 'bg-purple-100 text-purple-800'
    case 'resolved':        return 'bg-green-100 text-green-800'
    case 'escalated':       return 'bg-red-100 text-red-800'
    default:                return 'bg-gray-100 text-gray-700'
  }
}

export function policyColor(policy: string) {
  switch (policy?.toLowerCase()) {
    case 'allow':  return 'bg-green-100 text-green-700'
    case 'review': return 'bg-yellow-100 text-yellow-700'
    case 'block':  return 'bg-red-100 text-red-700'
    default:       return 'bg-gray-100 text-gray-700'
  }
}

export function paymentStatusColor(status: string) {
  switch (status) {
    case 'captured':    return 'bg-green-100 text-green-800'
    case 'failed':      return 'bg-red-100 text-red-800'
    case 'authorized':  return 'bg-blue-100 text-blue-800'
    case 'timeout':     return 'bg-orange-100 text-orange-800'
    case 'refunded':    return 'bg-purple-100 text-purple-800'
    default:            return 'bg-gray-100 text-gray-700'
  }
}
