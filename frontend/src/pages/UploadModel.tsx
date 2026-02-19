import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { modelsAPI } from '../services/api'
import toast from 'react-hot-toast'
import { Upload } from 'lucide-react'

export default function UploadModel() {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [framework, setFramework] = useState('scikit-learn')
  const [version, setVersion] = useState('1.0.0')
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      toast.error('Please select a model file')
      return
    }

    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('name', name)
      formData.append('description', description)
      formData.append('framework', framework)
      formData.append('version', version)

      await modelsAPI.upload(formData)
      toast.success('Model uploaded successfully')
      navigate('/models')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Upload Model</h1>

      <div className="max-w-2xl bg-white p-8 rounded-xl shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">Model Name</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="My ML Model"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              rows={3}
              className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Describe your model..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Framework</label>
              <select
                value={framework}
                onChange={e => setFramework(e.target.value)}
                className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="scikit-learn">scikit-learn</option>
                <option value="tensorflow">TensorFlow</option>
                <option value="pytorch">PyTorch</option>
                <option value="xgboost">XGBoost</option>
                <option value="lightgbm">LightGBM</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Version</label>
              <input
                type="text"
                value={version}
                onChange={e => setVersion(e.target.value)}
                className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="1.0.0"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Model File</label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-primary-400">
              <div className="space-y-1 text-center">
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <div className="flex text-sm text-gray-600">
                  <label className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-700">
                    <span>Upload a file</span>
                    <input
                      type="file"
                      accept=".joblib,.pkl,.h5,.pt,.pth"
                      onChange={e => setFile(e.target.files?.[0] || null)}
                      className="sr-only"
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-gray-500">
                  .joblib, .pkl, .h5, .pt, .pth up to 100MB
                </p>
              </div>
            </div>
            {file && (
              <p className="mt-2 text-sm text-green-600">
                Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 focus:ring-4 focus:ring-primary-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Uploading...' : 'Upload Model'}
          </button>
        </form>
      </div>
    </div>
  )
}
