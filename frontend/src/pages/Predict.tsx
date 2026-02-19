import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { modelsAPI } from '../services/api'
import toast from 'react-hot-toast'
import { Brain, ArrowLeft } from 'lucide-react'

export default function Predict() {
  const { modelId } = useParams()
  const navigate = useNavigate()
  const [models, setModels] = useState<any[]>([])
  const [selectedModel, setSelectedModel] = useState<number | null>(null)
  const [inputData, setInputData] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [modelsLoading, setModelsLoading] = useState(true)

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await modelsAPI.list()
        setModels(response.data)
        if (modelId) {
          setSelectedModel(parseInt(modelId))
        } else if (response.data.length > 0) {
          setSelectedModel(response.data[0].id)
        }
      } catch (error) {
        toast.error('Failed to load models')
      } finally {
        setModelsLoading(false)
      }
    }
    fetchModels()
  }, [modelId])

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedModel) {
      toast.error('Please select a model')
      return
    }

    let parsedInput
    try {
      parsedInput = JSON.parse(inputData)
    } catch {
      toast.error('Invalid JSON format')
      return
    }

    setLoading(true)
    try {
      const response = await modelsAPI.predict(selectedModel, parsedInput)
      setResult(response.data)
      toast.success('Prediction successful')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Prediction failed')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <Link to="/models" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="h-5 w-5 text-gray-600" />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Make Prediction</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Model & Input</h2>
          
          <form onSubmit={handlePredict} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Select Model</label>
              {modelsLoading ? (
                <div className="h-12 bg-gray-100 rounded-lg animate-pulse"></div>
              ) : models.length === 0 ? (
                <p className="text-gray-500">No models available. <Link to="/upload" className="text-primary-600">Upload one first</Link></p>
              ) : (
                <select
                  value={selectedModel || ''}
                  onChange={e => setSelectedModel(parseInt(e.target.value))}
                  className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  {models.map(model => (
                    <option key={model.id} value={model.id}>
                      {model.name} ({model.framework})
                    </option>
                  ))}
                </select>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Input Data (JSON)</label>
              <textarea
                value={inputData}
                onChange={e => setInputData(e.target.value)}
                rows={8}
                className="font-mono text-sm block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder='{"feature1": 1.0, "feature2": 2.0}'
              />
            </div>

            <button
              type="submit"
              disabled={loading || !selectedModel}
              className="w-full py-3 px-4 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 focus:ring-4 focus:ring-primary-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <Brain className="h-5 w-5" />
              {loading ? 'Predicting...' : 'Make Prediction'}
            </button>
          </form>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Result</h2>
          
          {result ? (
            <div className="space-y-4">
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-800 font-medium">Prediction</p>
                <pre className="mt-2 text-sm font-mono text-green-900 overflow-x-auto">
                  {JSON.stringify(result.predictions, null, 2)}
                </pre>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Model</p>
                  <p className="font-medium text-gray-900">{result.model_name}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Prediction Time</p>
                  <p className="font-medium text-gray-900">{result.prediction_time.toFixed(3)}s</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Brain className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <p>Select a model and enter input data to see predictions</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
