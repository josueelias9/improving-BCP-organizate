'use client'

import { useActionState } from 'react'
import { updateTransaction, TransactionState } from '@/app/lib/actions'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useEffect, useRef } from 'react'

interface EditTransactionModalProps {
    transaction: {
        id: string
        category_name?: string
        history?: string
    }
    isOpen: boolean
    onClose: () => void
}

export default function EditTransactionModal({
    transaction,
    isOpen,
    onClose
}: EditTransactionModalProps) {
    const initialState: TransactionState = { message: null, errors: {} }
    const updateTransactionWithId = updateTransaction.bind(null, transaction.id)
    const [state, dispatch] = useActionState(updateTransactionWithId, initialState)
    const modalRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
                onClose()
            }
        }

        const handleEscape = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                onClose()
            }
        }

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside)
            document.addEventListener('keydown', handleEscape)
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside)
            document.removeEventListener('keydown', handleEscape)
        }
    }, [isOpen, onClose])

    useEffect(() => {
        if (state.message && !state.errors) {
            // Success - close modal after 1 second
            const timer = setTimeout(() => {
                onClose()
            }, 1000)
            return () => clearTimeout(timer)
        }
    }, [state.message, state.errors, onClose])

    if (!isOpen) return null

    return (
        <div className='fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50'>
            <div
                ref={modalRef}
                className='relative w-full max-w-md rounded-lg bg-white p-6 shadow-xl'
            >
                <button
                    onClick={onClose}
                    className='absolute right-4 top-4 text-gray-400 hover:text-gray-600'
                    aria-label='Close'
                >
                    <XMarkIcon className='h-6 w-6' />
                </button>

                <h2 className='mb-6 text-xl font-semibold text-gray-900'>Edit Transaction</h2>

                <form action={dispatch} className='space-y-4'>
                    <div>
                        <label
                            htmlFor='category_name'
                            className='mb-2 block text-sm font-medium text-gray-700'
                        >
                            Category Name *
                        </label>
                        <input
                            id='category_name'
                            name='category_name'
                            type='text'
                            defaultValue={transaction.category_name || ''}
                            className='block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500'
                            aria-describedby='category_name-error'
                        />
                        {state.errors?.category_name && (
                            <div id='category_name-error' className='mt-2 text-sm text-red-500'>
                                {state.errors.category_name.map((error: string) => (
                                    <p key={error}>{error}</p>
                                ))}
                            </div>
                        )}
                    </div>

                    <div>
                        <label
                            htmlFor='history'
                            className='mb-2 block text-sm font-medium text-gray-700'
                        >
                            History
                        </label>
                        <textarea
                            id='history'
                            name='history'
                            rows={4}
                            defaultValue={transaction.history || ''}
                            className='block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500'
                            aria-describedby='history-error'
                        />
                        {state.errors?.history && (
                            <div id='history-error' className='mt-2 text-sm text-red-500'>
                                {state.errors.history.map((error: string) => (
                                    <p key={error}>{error}</p>
                                ))}
                            </div>
                        )}
                    </div>

                    {state.message && (
                        <div
                            className={`rounded-md px-4 py-2 text-sm ${
                                state.errors
                                    ? 'bg-red-50 text-red-800'
                                    : 'bg-green-50 text-green-800'
                            }`}
                        >
                            {state.message}
                        </div>
                    )}

                    <div className='flex justify-end gap-3 pt-4'>
                        <button
                            type='button'
                            onClick={onClose}
                            className='rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                        >
                            Cancel
                        </button>
                        <button
                            type='submit'
                            className='rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                        >
                            Save Changes
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
