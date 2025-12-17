'use client'

interface FilterSelectProps {
    id: string
    label: string
    value: string
    options: string[]
    onChange: (value: string) => void
    placeholder?: string
}

export default function FilterSelect({
    id,
    label,
    value,
    options,
    onChange,
    placeholder = 'All'
}: FilterSelectProps) {
    return (
        <div>
            <label htmlFor={id} className='block text-sm font-medium text-gray-700 mb-2'>
                {label}
            </label>
            <select
                id={id}
                value={value}
                onChange={e => onChange(e.target.value)}
                className='w-full rounded-md border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500'
            >
                <option value=''>{placeholder}</option>
                {options.map(option => (
                    <option key={option} value={option}>
                        {option}
                    </option>
                ))}
            </select>
        </div>
    )
}
