'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface APIKey {
  id: string;
  name: string;
  key_prefix: string;
  created_at: string;
  last_used_at: string | null;
  expires_at: string | null;
}

export default function APIKeysPage() {
  const router = useRouter();
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyValue, setNewKeyValue] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    fetchAPIKeys();
  }, []);

  const fetchAPIKeys = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/api-keys`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await res.json();
      setApiKeys(data);
    } catch (error) {
      console.error('Failed to fetch API keys:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);

    const token = localStorage.getItem('access_token');

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/api-keys`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ name: newKeyName }),
      });

      const data = await res.json();
      setNewKeyValue(data.api_key);
      setNewKeyName('');
      await fetchAPIKeys();
    } catch (error) {
      console.error('Failed to create API key:', error);
    } finally {
      setCreating(false);
    }
  };

  const handleRevokeKey = async (id: string) => {
    if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
      return;
    }

    const token = localStorage.getItem('access_token');

    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/api-keys/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      await fetchAPIKeys();
    } catch (error) {
      console.error('Failed to revoke API key:', error);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">API Keys</h1>
          <p className="text-gray-600 mt-1">Manage your API keys for programmatic access</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition flex items-center gap-2"
        >
          <span>+</span>
          <span>Create API Key</span>
        </button>
      </div>

      {/* New Key Display */}
      {newKeyValue && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-6">
          <h3 className="font-semibold text-green-900 mb-2">API Key Created Successfully!</h3>
          <p className="text-sm text-green-700 mb-4">
            Make sure to copy your API key now. You won't be able to see it again!
          </p>
          <div className="bg-white border border-green-300 rounded-lg p-4 flex items-center justify-between">
            <code className="text-sm font-mono text-gray-900">{newKeyValue}</code>
            <button
              onClick={() => copyToClipboard(newKeyValue)}
              className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-semibold hover:bg-green-700 transition"
            >
              Copy
            </button>
          </div>
          <button
            onClick={() => setNewKeyValue('')}
            className="mt-4 text-sm text-green-700 hover:text-green-800 font-medium"
          >
            Close
          </button>
        </div>
      )}

      {/* Create Form */}
      {showCreateForm && !newKeyValue && (
        <form onSubmit={handleCreateKey} className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Create New API Key</h3>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Key Name
            </label>
            <input
              type="text"
              required
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              placeholder="e.g., Production Server, Development, CI/CD"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-600 mt-1">
              Choose a descriptive name to identify where this key will be used
            </p>
          </div>
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={creating}
              className="px-6 py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition disabled:opacity-50"
            >
              {creating ? 'Creating...' : 'Create Key'}
            </button>
            <button
              type="button"
              onClick={() => setShowCreateForm(false)}
              className="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* API Keys List */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Your API Keys</h2>

        {apiKeys.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
            <div className="text-6xl mb-4">🔑</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No API keys yet</h3>
            <p className="text-gray-600 mb-6">Create your first API key to access the platform programmatically</p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="inline-block px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition"
            >
              Create API Key
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {apiKeys.map((key) => (
              <div
                key={key.id}
                className="bg-white rounded-xl border border-gray-200 p-6 hover:border-purple-300 transition"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">{key.name}</h3>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span className="font-mono bg-gray-100 px-2 py-1 rounded">
                        {key.key_prefix}...
                      </span>
                      <span>Created {new Date(key.created_at).toLocaleDateString()}</span>
                      {key.last_used_at && (
                        <span>Last used {new Date(key.last_used_at).toLocaleDateString()}</span>
                      )}
                      {key.expires_at && (
                        <span className="text-orange-600">
                          Expires {new Date(key.expires_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => handleRevokeKey(key.id)}
                    className="px-4 py-2 bg-red-50 text-red-600 rounded-lg text-sm font-semibold hover:bg-red-100 transition"
                  >
                    Revoke
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Documentation */}
      <div className="bg-white rounded-xl border border-gray-200 p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Using API Keys</h2>
        <div className="space-y-4 text-sm text-gray-700">
          <p>
            Use your API key to authenticate requests to the Echo AI API. Include it in the Authorization header:
          </p>
          <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto">
            {`curl -H "Authorization: Bearer YOUR_API_KEY" \\
  ${process.env.NEXT_PUBLIC_API_URL}/api/v1/experiments`}
          </pre>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h4 className="font-semibold text-yellow-900 mb-1">Security Best Practices</h4>
            <ul className="space-y-1 text-yellow-800 text-sm">
              <li>• Never share your API keys publicly</li>
              <li>• Store keys securely in environment variables</li>
              <li>• Rotate keys regularly</li>
              <li>• Use different keys for different environments</li>
              <li>• Revoke keys immediately if compromised</li>
            </ul>
          </div>
          <p>
            For full API documentation, visit our{' '}
            <a href="/docs/api" className="text-purple-600 hover:text-purple-700 font-medium">
              API Reference
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
