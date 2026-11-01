import {render, screen} from '@testing-library/react'
import {describe, expect, it} from 'vitest'
function Brand(){ return <h1>Mente Segura</h1> }
describe('Identidad visual',()=>{
it('muestra el nombre de la aplicación',()=>{
render(<Brand />)
expect(screen.getByText('Mente Segura')).toBeTruthy()
})
})
