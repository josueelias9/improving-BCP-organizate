'use client'

import { useState } from 'react'
import { formatCurrency } from '@/app/lib/utils'
import { lusitana } from '@/app/ui/fonts'
import EditTransactionModal from '@/app/ui/dashboard/transactions/edit-transaction-modal'
import FilterSelect from '@/app/ui/dashboard/transactions/filter-select'
import type { Category } from '@/app/lib/definitions'
import { exportTransactionsToCSV, importTransactionsFromCSV } from '@/app/lib/actions'
import { ArrowDownTrayIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline'

function formatTransactionDate(dateString: string) {
    try {
        const date = new Date(dateString)
        if (isNaN(date.getTime())) {
            return dateString // Return original if invalid
        }
        return new Intl.DateTimeFormat('en-US', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        }).format(date)
    } catch {
        return dateString
    }
}

export default function TransactionsTable({
    transactions,
    categories
}: {
    transactions: any[]
    categories: Category[]
}) {
    const [selectedTransaction, setSelectedTransaction] = useState<any>(null)
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [hoveredRow, setHoveredRow] = useState<string | null>(null)
    const [showEditTooltip, setShowEditTooltip] = useState(false)
    const [filterDocumentType, setFilterDocumentType] = useState('')
    const [filterTransactionType, setFilterTransactionType] = useState('')
    const [filterCategoryName, setFilterCategoryName] = useState('')
    const [isExporting, setIsExporting] = useState(false)
    const [isImporting, setIsImporting] = useState(false)
    const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null)

    // Get unique values for combo boxes
    const uniqueDocumentTypes = Array.from(
        new Set(
            transactions.map(t => t.document_type_name).filter(name => name) // Remove null/undefined values
        )
    ).sort()

    const uniqueTransactionTypes = Array.from(
        new Set(
            transactions.map(t => t.transaction_type).filter(type => type) // Remove null/undefined values
        )
    ).sort()

    const uniqueCategoryNames = Array.from(
        new Set(
            transactions.map(t => t.category_name).filter(name => name) // Remove null/undefined values
        )
    ).sort()

    // Filter transactions by all active filters
    const filteredTransactions = transactions.filter(t => {
        if (filterDocumentType && t.document_type_name !== filterDocumentType) return false
        if (filterTransactionType && t.transaction_type !== filterTransactionType) return false
        if (filterCategoryName && t.category_name !== filterCategoryName) return false
        return true
    })

    // Sort transactions by 'order' column if it exists
    const sortedTransactions = [...filteredTransactions].sort((a, b) => {
        if (a.order !== undefined && b.order !== undefined) {
            return a.order - b.order
        }
        return 0
    })

    const handleRowClick = (transaction: any) => {
        setSelectedTransaction(transaction)
        setIsModalOpen(true)
    }

    const handleMouseEnter = (transactionId: string) => {
        setHoveredRow(transactionId)
        const timer = setTimeout(() => {
            setShowEditTooltip(true)
        }, 1000)
        return () => clearTimeout(timer)
    }

    const handleMouseLeave = () => {
        setHoveredRow(null)
        setShowEditTooltip(false)
    }

    // Check if transaction needs completion (missing history or category_name)
    const isIncomplete = (transaction: any) => {
        return !transaction.history || !transaction.category_name
    }

    const handleExportCSV = async () => {
        setIsExporting(true)
        setMessage(null)

        const result = await exportTransactionsToCSV()

        setIsExporting(false)
        setMessage({
            text: result.message,
            type: result.success ? 'success' : 'error'
        })

        setTimeout(() => setMessage(null), 5000)
    }

    const handleImportCSV = async () => {
        setIsImporting(true)
        setMessage(null)

        const result = await importTransactionsFromCSV()

        setIsImporting(false)
        setMessage({
            text: result.message,
            type: result.success ? 'success' : 'error'
        })

        setTimeout(() => setMessage(null), 5000)

        // Reload page if successful to show updated data
        if (result.success) {
            setTimeout(() => window.location.reload(), 2000)
        }
    }

    const not_included_columns = [
        'unique_identifier',
        'id',
        'document_id',
        'category_id',
        'user_id',
        'document_type_name',
        'transaction_type'
    ]

    // Get column names from the first transaction
    const columns =
        sortedTransactions.length > 0
            ? Object.keys(sortedTransactions[0]).filter(col => !not_included_columns.includes(col))
            : []

    return (
        <div className='flex w-full flex-col md:col-span-4'>
            <div className='flex items-center justify-between mb-4'>
                <h2 className={`${lusitana.className} text-xl md:text-2xl`}>All Transactions</h2>

                {/* CSV Export/Import buttons */}
                <div className='flex gap-2'>
                    <button
                        onClick={handleExportCSV}
                        disabled={isExporting}
                        className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                            isExporting
                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                : 'bg-green-600 text-white hover:bg-green-700'
                        }`}
                        title='Export transactions to CSV'
                    >
                        <ArrowDownTrayIcon
                            className={`h-5 w-5 ${isExporting ? 'animate-bounce' : ''}`}
                        />
                        {isExporting ? 'Exporting...' : 'Export CSV'}
                    </button>

                    <button
                        onClick={handleImportCSV}
                        disabled={isImporting}
                        className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                            isImporting
                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                        title='Import transactions from CSV'
                    >
                        <ArrowUpTrayIcon
                            className={`h-5 w-5 ${isImporting ? 'animate-bounce' : ''}`}
                        />
                        {isImporting ? 'Importing...' : 'Import CSV'}
                    </button>
                </div>
            </div>

            {/* Success/Error message */}
            {message && (
                <div
                    className={`mb-4 rounded-md px-4 py-3 text-sm ${
                        message.type === 'success'
                            ? 'bg-green-50 text-green-800'
                            : 'bg-red-50 text-red-800'
                    }`}
                >
                    {message.text}
                </div>
            )}

            {/* Filters */}
            <div className='mb-4 grid grid-cols-1 md:grid-cols-3 gap-4'>
                <FilterSelect
                    id='filter-document-type'
                    label='Filter by Document Type'
                    value={filterDocumentType}
                    options={uniqueDocumentTypes}
                    onChange={setFilterDocumentType}
                    placeholder='All Document Types'
                />

                <FilterSelect
                    id='filter-transaction-type'
                    label='Filter by Transaction Type'
                    value={filterTransactionType}
                    options={uniqueTransactionTypes}
                    onChange={setFilterTransactionType}
                    placeholder='All Transaction Types'
                />

                <FilterSelect
                    id='filter-category-name'
                    label='Filter by Category'
                    value={filterCategoryName}
                    options={uniqueCategoryNames}
                    onChange={setFilterCategoryName}
                    placeholder='All Categories'
                />
            </div>

            <div className='flex grow flex-col justify-between rounded-xl bg-gray-50 p-4'>
                <div className='overflow-x-auto'>
                    <table className='min-w-full text-gray-900'>
                        <thead className='rounded-lg text-left text-sm font-normal'>
                            <tr>
                                {columns.map(column => (
                                    <th key={column} scope='col' className='px-3 py-5 font-medium'>
                                        {column}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className='bg-white'>
                            {sortedTransactions.map(transaction => {
                                const incomplete = isIncomplete(transaction)
                                const bgColor = incomplete ? 'bg-yellow-50' : 'bg-green-50'
                                const hoverColor = incomplete
                                    ? 'hover:bg-yellow-100'
                                    : 'hover:bg-green-100'

                                return (
                                    // TODO: evaluate if we can also send the id from the backend as an identifier because it is required for JSX keys
                                    <tr
                                        key={transaction.order}
                                        onClick={() => handleRowClick(transaction)}
                                        onMouseEnter={() => handleMouseEnter(transaction.id)}
                                        onMouseLeave={handleMouseLeave}
                                        className={`w-full border-b py-3 text-sm last-of-type:border-none cursor-pointer transition-colors ${
                                            hoveredRow === transaction.id
                                                ? incomplete
                                                    ? 'bg-yellow-100'
                                                    : 'bg-green-100'
                                                : bgColor
                                        } ${hoverColor} [&:first-child>td:first-child]:rounded-tl-lg [&:first-child>td:last-child]:rounded-tr-lg [&:last-child>td:first-child]:rounded-bl-lg [&:last-child>td:last-child]:rounded-br-lg`}
                                    >
                                        {columns.map((column, index) => {
                                            const value =
                                                transaction[column as keyof typeof transaction]
                                            let displayValue: React.ReactNode = value ?? ''
                                            const isEditableColumn =
                                                column === 'history' || column === 'category_name'

                                            // Special formatting for specific columns
                                            if (column === 'amount') {
                                                displayValue = (
                                                    <span
                                                        className={`inline-flex items-center rounded-full px-2 py-1 text-xs ${
                                                            (value as number) >= 0
                                                                ? 'bg-green-100 text-green-700'
                                                                : 'bg-red-100 text-red-700'
                                                        }`}
                                                    >
                                                        {formatCurrency((value as number) || 0)}
                                                    </span>
                                                )
                                            } else if (
                                                column === 'transaction_date' ||
                                                column === 'created_at'
                                            ) {
                                                displayValue = formatTransactionDate(
                                                    value as string
                                                )
                                            } else if (
                                                typeof value === 'string' &&
                                                value.length > 20
                                            ) {
                                                // Truncate long strings (like IDs)
                                                displayValue = (
                                                    <div
                                                        className='truncate max-w-[150px]'
                                                        title={value}
                                                    >
                                                        {value.substring(0, 15)}...
                                                    </div>
                                                )
                                            }

                                            const isLastColumn = index === columns.length - 1

                                            return (
                                                <td
                                                    key={column}
                                                    className={`whitespace-nowrap px-3 py-3 ${isLastColumn ? 'relative' : ''} ${
                                                        isEditableColumn
                                                            ? 'font-semibold border-l-2 border-blue-400'
                                                            : ''
                                                    }`}
                                                >
                                                    {isEditableColumn && !value && (
                                                        <span className='text-gray-400 italic text-xs'>
                                                            Click to edit
                                                        </span>
                                                    )}
                                                    {value && displayValue}
                                                    {isLastColumn &&
                                                        hoveredRow === transaction.id &&
                                                        showEditTooltip && (
                                                            <span className='absolute right-4 top-1/2 -translate-y-1/2 rounded bg-blue-600 px-3 py-1.5 text-xs text-white shadow-lg pointer-events-none'>
                                                                ✏️ Click to edit History & Category
                                                            </span>
                                                        )}
                                                </td>
                                            )
                                        })}
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                    {sortedTransactions.length === 0 && (
                        <div className='flex items-center justify-center py-10'>
                            <p className='text-gray-500'>No transactions found.</p>
                        </div>
                    )}
                </div>
                <div className='flex items-center pt-6'>
                    <p className='text-sm text-gray-500'>
                        Total: {sortedTransactions.length} transaction
                        {sortedTransactions.length !== 1 ? 's' : ''}
                    </p>
                </div>
            </div>

            {selectedTransaction && (
                <EditTransactionModal
                    transaction={selectedTransaction}
                    isOpen={isModalOpen}
                    onClose={() => {
                        setIsModalOpen(false)
                        setSelectedTransaction(null)
                    }}
                    categories={categories}
                />
            )}
        </div>
    )
}
