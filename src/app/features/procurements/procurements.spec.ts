import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Procurements } from './procurements';

describe('Procurements', () => {
  let component: Procurements;
  let fixture: ComponentFixture<Procurements>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Procurements],
    }).compileComponents();

    fixture = TestBed.createComponent(Procurements);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
