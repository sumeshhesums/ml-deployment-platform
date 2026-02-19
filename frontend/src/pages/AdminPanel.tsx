import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { api } from '../services/api'
import { Users, Brain, Activity, AlertCircle, Clock } from 'lucide-react'

interface Stats {
  users: { total_users: number; active_users: number }
  models: { total_models: number; total_predictions: number }
  analytics: {
    total_predictions: number
    avg_prediction_time: number
    success_rate: number
    daily_predictions: Record<string, number>
    status_counts: Record<string, number>
  }
}

export default function AdminPanel() {
  const { user } = useAuth()
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user?.is_admin) {
      api.get('/admin/stats')
        .then(res => setStats(res.data))
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [user])

  if (!user?.is_admin) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-16 w-16 text-red-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900">Access Denied</h2>
          <p className="text-gray-500">You don't have permission to view this page.</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-1/4"></div>
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map(i => <div key={i} className="h-24 bg-gray-200 rounded"></div>)}
        </div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Admin Panel</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-500 rounded-lg">
              <Users className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Users</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.users?.total_users || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-500 rounded-lg">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Models</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.models?.total_models || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-500 rounded-lg">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Predictions</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.analytics?.total_predictions || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-yellow-500 rounded-lg">
              <Clock className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Avg Time (ms)</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.analytics?.avg_prediction_time ? (stats.analytics.avg_prediction_time * 1000).toFixed(2) : 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Prediction Status</h2>
          <div className="space-y-3">
            {stats?.analytics?.status_counts && Object.entries(stats.analytics.status_counts).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between">
                <span className="text-gray-600 capitalize">{status}</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full ${status === 'success' ? 'bg-green-500' : 'bg-red-500'}`}
                      style={{ width: `${(count / (stats.analytics.total_predictions || 1)) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t">
            <div className="flex justify-between">
              <span className="text-gray-600">Success Rate</span>
              <span className="font-semibold text-green-600">{stats?.analytics?.success_rate?.toFixed(1) || 0}%</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h2>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-gray-500">Active Users</dt>
              <dd className="font-medium text-gray-900">{stats?.users?.active_users || 0}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Total Predictions</dt>
              <dd className="font-medium text-gray-900">{stats?.models?.total_predictions || 0}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  )
}
