import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { modelsAPI } from '../services/api'
import toast from 'react-hot-toast'
import { Brain, Trash2, BarChart3 } from 'lucide-react'

export default function ModelList() {
  const [models, setModels] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchModels = async () => {
    try {
      const response = await modelsAPI.list()
      setModels(response.data)
    } catch (error) {
      toast.error('Failed to load models')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchModels()
  }, [])

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return
    try {
      await modelsAPI.delete(id)
      toast.success('Model deleted')
      fetchModels()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Delete failed')
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My Models</h1>
        <Link
          to="/upload"
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Upload New
        </Link>
      </div>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8">
            <div className="animate-pulse space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-16 bg-gray-100 rounded"></div>
              ))}
            </div>
          </div>
        ) : models.length === 0 ? (
          <div className="p-8 text-center">
            <Brain className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No models uploaded yet</p>
            <Link
              to="/upload"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Upload your first model
            </Link>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Framework</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Version</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Predictions</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {models.map(model => (
                <tr key={model.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{model.name}</div>
                    <div className="text-sm text-gray-500">{model.model_type}</div>
                  </td>
                  <td className="px-6 py-4 text-gray-600">{model.framework}</td>
                  <td className="px-6 py-4 text-gray-600">v{model.version}</td>
                  <td className="px-6 py-4 text-gray-600">{model.usage_count}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded ${model.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                      {model.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex justify-end gap-2">
                      <Link
                        to={`/predict/${model.id}`}
                        className="p-2 text-primary-600 hover:bg-primary-50 rounded"
                        title="Predict"
                      >
                        <Brain className="h-5 w-5" />
                      </Link>
                      <Link
                        to={`/stats/${model.id}`}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                        title="Stats"
                      >
                        <BarChart3 className="h-5 w-5" />
                      </Link>
                      <button
                        onClick={() => handleDelete(model.id, model.name)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded"
                        title="Delete"
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
