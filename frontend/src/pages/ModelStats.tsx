import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { modelsAPI } from '../services/api'
import toast from 'react-hot-toast'
import { ArrowLeft, BarChart3, Clock } from 'lucide-react'

export default function ModelStats() {
  const { modelId } = useParams()
  const [stats, setStats] = useState<any>(null)
  const [history, setHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [statsRes, historyRes] = await Promise.all([
          modelsAPI.getStats(parseInt(modelId!)),
          modelsAPI.getHistory(parseInt(modelId!))
        ])
        setStats(statsRes.data)
        setHistory(historyRes.data)
      } catch (error) {
        toast.error('Failed to load stats')
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [modelId])

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-3 gap-4">
            <div className="h-24 bg-gray-200 rounded"></div>
            <div className="h-24 bg-gray-200 rounded"></div>
            <div className="h-24 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <Link to="/models" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="h-5 w-5 text-gray-600" />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Model Statistics</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-500 rounded-lg">
              <BarChart3 className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Predictions</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.statistics?.usage_count || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-500 rounded-lg">
              <Clock className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Uploaded</p>
              <p className="text-lg font-bold text-gray-900">
                {new Date(stats?.statistics?.upload_date).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-500 rounded-lg">
              <BarChart3 className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Version</p>
              <p className="text-2xl font-bold text-gray-900">v{stats?.model_info?.version}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Model Details</h2>
        <dl className="grid grid-cols-2 gap-4">
          <div>
            <dt className="text-sm text-gray-500">Name</dt>
            <dd className="font-medium text-gray-900">{stats?.model_info?.name}</dd>
          </div>
          <div>
            <dt className="text-sm text-gray-500">Framework</dt>
            <dd className="font-medium text-gray-900">{stats?.model_info?.framework}</dd>
          </div>
          <div>
            <dt className="text-sm text-gray-500">Model Type</dt>
            <dd className="font-medium text-gray-900">{stats?.model_info?.model_type}</dd>
          </div>
          <div>
            <dt className="text-sm text-gray-500">Status</dt>
            <dd className="font-medium">
              <span className={`px-2 py-1 text-xs rounded ${stats?.model_info?.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                {stats?.model_info?.is_active ? 'Active' : 'Inactive'}
              </span>
            </dd>
          </div>
        </dl>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-sm mt-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Predictions</h2>
        {history.length === 0 ? (
          <p className="text-gray-500">No predictions yet</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Time</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Input</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Output</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Duration</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {history.slice(0, 10).map((pred: any) => (
                  <tr key={pred.id}>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      {new Date(pred.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-2 text-sm font-mono text-gray-600 max-w-xs truncate">
                      {pred.input_data}
                    </td>
                    <td className="px-4 py-2 text-sm font-mono text-gray-900 max-w-xs truncate">
                      {pred.output_data}
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      {pred.prediction_time?.toFixed(3)}s
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
