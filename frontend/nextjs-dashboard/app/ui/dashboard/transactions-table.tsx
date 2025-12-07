import { fetchTransactions } from '@/app/lib/data'
import { formatCurrency } from '@/app/lib/utils'
import { lusitana } from '@/app/ui/fonts'

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

export default async function TransactionsTable() {
    const transactions = await fetchTransactions()

    const not_included_columns = ["unique_identifier","created_at","updated_at","id"]
    
    // Get column names from the first transaction
    const columns = transactions.length > 0 
        ? Object.keys(transactions[0]).filter(col => !not_included_columns.includes(col))
        : []

    return (
        <div className='flex w-full flex-col md:col-span-4'>
            <h2 className={`${lusitana.className} mb-4 text-xl md:text-2xl`}>
                All Transactions
            </h2>
            <div className='flex grow flex-col justify-between rounded-xl bg-gray-50 p-4'>
                <div className='overflow-x-auto'>
                    <table className='min-w-full text-gray-900'>
                        <thead className='rounded-lg text-left text-sm font-normal'>
                            <tr>
                                {columns.map((column) => (
                                    <th key={column} scope='col' className='px-3 py-5 font-medium'>
                                        {column}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className='bg-white'>
                            {transactions.map((transaction) => (
                                <tr
                                    key={transaction.id}
                                    className='w-full border-b py-3 text-sm last-of-type:border-none [&:first-child>td:first-child]:rounded-tl-lg [&:first-child>td:last-child]:rounded-tr-lg [&:last-child>td:first-child]:rounded-bl-lg [&:last-child>td:last-child]:rounded-br-lg'
                                >
                                    {columns.map((column) => {
                                        const value = transaction[column as keyof typeof transaction]
                                        let displayValue: React.ReactNode = value || 'N/A'

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
                                        } else if (column === 'transaction_date' || column === 'created_at') {
                                            displayValue = formatTransactionDate(value as string)
                                        } else if (typeof value === 'string' && value.length > 20) {
                                            // Truncate long strings (like IDs)
                                            displayValue = (
                                                <div className='truncate max-w-[150px]' title={value}>
                                                    {value.substring(0, 15)}...
                                                </div>
                                            )
                                        }

                                        return (
                                            <td key={column} className='whitespace-nowrap px-3 py-3'>
                                                {displayValue}
                                            </td>
                                        )
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {transactions.length === 0 && (
                        <div className='flex items-center justify-center py-10'>
                            <p className='text-gray-500'>No transactions found.</p>
                        </div>
                    )}
                </div>
                <div className='flex items-center pt-6'>
                    <p className='text-sm text-gray-500'>
                        Total: {transactions.length} transaction{transactions.length !== 1 ? 's' : ''}
                    </p>
                </div>
            </div>
        </div>
    )
}
