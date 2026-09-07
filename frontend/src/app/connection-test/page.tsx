'use client'

import { useEffect, useState } from 'react'
import { API_URL } from '@/../lib/api'

export default function ConnectionTest() {
  const [fastApiStatus, setFastApiStatus] = useState<string>('Testing...')
  const [supabaseStatus, setSupabaseStatus] = useState<string>('Testing...')

  useEffect(() => {
    async function testFastAPI() {
      try {
        const res = await fetch(`${API_URL}/api/health`)
        if (res.ok) {
          setFastApiStatus('Connected')
        } else {
          setFastApiStatus('Error: Bad Response')
        }
      } catch (err) {
        setFastApiStatus('Error: ' + String(err))
      }
    }

    async function testSupabase() {
      try {
        const res = await fetch(`${API_URL}/api/test/supabase`)
        if (res.ok) {
          const data = await res.json()
          if (data.status === 'success') {
            setSupabaseStatus('Connected')
          } else {
            setSupabaseStatus('Configured but table unavailable or connection failed')
          }
        } else {
          setSupabaseStatus('Error: Bad Response')
        }
      } catch (err) {
        setSupabaseStatus('Error: ' + String(err))
      }
    }

    testFastAPI()
    testSupabase()
  }, [])

  return (
    <div className="p-8 font-sans">
      <h1 className="text-2xl font-bold mb-4">Connection Test</h1>
      
      <div className="mb-4 p-4 border rounded shadow-sm">
        <h2 className="text-xl font-semibold">Frontend → FastAPI</h2>
        <p className="mt-2">Status: <span className="font-mono bg-gray-100 px-2 py-1 rounded">{fastApiStatus}</span></p>
      </div>

      <div className="p-4 border rounded shadow-sm">
        <h2 className="text-xl font-semibold">FastAPI → Supabase</h2>
        <p className="mt-2">Status: <span className="font-mono bg-gray-100 px-2 py-1 rounded">{supabaseStatus}</span></p>
      </div>
    </div>
  )
}
