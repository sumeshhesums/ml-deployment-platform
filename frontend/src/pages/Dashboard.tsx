import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { modelsAPI } from '../services/api'
import { Brain, Upload, BarChart3, Clock } from 'lucide-react'

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState({ totalModels: 0, totalPredictions: 0 })
  const [recentModels, setRecentModels] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [modelsRes] = await Promise.all([
          modelsAPI.list(0, 5)
        ])
        const models = modelsRes.data
        setRecentModels(models)
        setStats({ totalModels: models.length, totalPredictions: models.reduce((acc: number, m: any) => acc + (m.usage_count || 0), 0) })
      } catch (error) {
        console.error(error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const cards = [
    { title: 'Total Models', value: stats.totalModels, icon: Brain, color: 'bg-blue-500' },
    { title: 'Total Predictions', value: stats.totalPredictions, icon: BarChart3, color: 'bg-green-500' },
    { title: 'Active User', value: user?.username || 'N/A', icon: Clock, color: 'bg-purple-500' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {cards.map(card => (
          <div key={card.title} className="bg-white p-6 rounded-xl shadow-sm">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-lg ${card.color}`}>
                <card.icon className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-gray-500">{card.title}</p>
                <p className="text-2xl font-bold text-gray-900">{card.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Models</h2>
            <Link to="/models" className="text-primary-600 hover:text-primary-700 text-sm">View all</Link>
          </div>
          {loading ? (
            <div className="animate-pulse space-y-3">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-12 bg-gray-100 rounded"></div>
              ))}
            </div>
          ) : recentModels.length > 0 ? (
            <div className="space-y-3">
              {recentModels.map(model => (
                <div key={model.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{model.name}</p>
                    <p className="text-sm text-gray-500">{model.framework} - v{model.version}</p>
                  </div>
                  <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                    {model.usage_count} predictions
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Brain className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No models yet</p>
              <Link to="/upload" className="text-primary-600 hover:text-primary-700 text-sm">Upload your first model</Link>
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              to="/upload"
              className="flex items-center gap-3 p-4 bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100"
            >
              <Upload className="h-5 w-5" />
              <span className="font-medium">Upload New Model</span>
            </Link>
            <Link
              to="/predict"
              className="flex items-center gap-3 p-4 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100"
            >
              <Brain className="h-5 w-5" />
              <span className="font-medium">Make Prediction</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
